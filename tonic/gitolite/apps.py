from django.conf import settings
from django.apps import AppConfig
from git import Repo
from umarkdown import markdown

import logging
import paramiko
import os


logger = logging.getLogger(__name__)


# TODO:
# Add a management command to update DB from gitolite-admin

def git_init():
    gitolite_admin_dir = settings.GITOLITE_ADMIN_PATH

    # This is too wonky
    known_hosts_path = '/root/.ssh/known_hosts'

    # Check if known_hosts exists, add gitolite host keys if not
    if not os.path.exists(known_hosts_path):
        with open(known_hosts_path, 'a') as known_hosts:
            for keyfile in ["ssh_host_dsa_key.pub", "ssh_host_ecdsa_key.pub",
                      "ssh_host_ed25519_key.pub", "ssh_host_rsa_key.pub"]:
                key = open('/root/keys/' + keyfile, 'r')
                keydata = key.read().strip().split(' ')
                known_hosts.write('%s %s %s\n' % (settings.GITOLITE_HOST, keydata[0], keydata[1]))
                key.close()


    # Check if gitolite-admin exists
    repo = None
    #logger.warn("Initializing git repo")
    if os.path.exists(gitolite_admin_dir) and os.path.isdir(gitolite_admin_dir):
        #logger.warn("Found directory at " + gitolite_admin_dir)
        repo = Repo(gitolite_admin_dir)
    else:
        logger.warn("Cloning gitolite-admin to " + gitolite_admin_dir)
        # Clone the repo otherwise
        repo = Repo.clone_from(
            'git@' + settings.GITOLITE_HOST + ':gitolite-admin.git',
            to_path=gitolite_admin_dir
        )

    return repo


def git_add_key_file(key):
    from django.contrib.auth import get_user_model
    from users.models import RSA_Key
    User = get_user_model()

    if not isinstance(key, RSA_Key):
        raise TypeError("Expected RSA_Key object in first argument, got %s" % (str(type(key))))

    keyname_dir = os.path.join(settings.GITOLITE_ADMIN_PATH, 'keydir', key.name)

    if not os.path.exists(keyname_dir):
        os.makedirs(keyname_dir)

    user = key.user

    keypath = os.path.join(keyname_dir, user.username + '.pub')
    keyfile = open(keypath, 'w')
    keyfile.write(key.public)
    keyfile.close()

    # Commit it to gitolite
    repo = git_init()
    repo.index.add([keypath])
    repo.index.commit("Add user %s's ssh key \"%s.pub\"" % (user.username, key.name))
    # TODO: Handle error?
    repo.remote().push().raise_if_error()


def git_update_userrepos(user):
    from django.contrib.auth import get_user_model
    from .models import Repository
    User = get_user_model()

    if not isinstance(user, User):
        raise TypeError("Expected User object in first argument, got %s" % (str(type(user))))

    userconfpath = os.path.join(settings.GITOLITE_ADMIN_PATH, 'conf', user.username + '.cfg')

    userrepos = Repository.objects.filter(owner=user)
    userconf = open(userconfpath, 'w')
    userconf.write('\n\n'.join([repo.get_config() for repo in userrepos]) + '\n')
    userconf.close()

    # Commit it to gitolite
    repo = git_init()
    repo.index.add([userconfpath])
    repo.index.commit("Update user \"%s\" config" % (user.username))
    # TODO: Handle error?
    repo.remote().push().raise_if_error()


def git_get_file_content(repo, filename):
    from .models import Repository

    if not isinstance(repo, Repository):
        raise TypeError("Expected Repository object in first argument, got %s" % (str(type(repo))))

    if not isinstance(filename, str):
        raise TypeError("Expected str in second argument, got %s" % (str(type(filename))))

    repo_path = os.path.join(
        settings.GITOLITE_ADMIN_PATH, '..', 'git',
        'repositories', repo.owner.username, repo.name + '.git')
    filecontent = ""

    try:
        repo = Repo(repo_path)
        filecontent = repo.git.show('{}:{}'.format(repo.active_branch.name, filename))

    except:
        pass

    return filecontent


def git_get_readme_html(repo):
    return markdown(git_get_file_content(repo, "README.md"))

def git_get_tree(repo, subdir=None):
    from .models import Repository

    if not isinstance(repo, Repository):
        raise TypeError("Expected Repository object in first argument, got %s" % (str(type(repo))))

    repo_path = os.path.join(
        settings.GITOLITE_ADMIN_PATH, '..', 'git',
        'repositories', repo.owner.username, repo.name + '.git')
    tree = ([],[])

    try:
        repo = Repo(repo_path)
        tree = repo.tree()

        subdirs = []
        if isinstance(subdir,str):
            subdirs = subdir.split('/').reverse()

            while len(subdirs) > 0:
                d = subdirs.pop()
                dd = filter(tree.tree, lambda t: t.name == d)

                if len(dd) != 1:
                    return 404

                dd = dd[0]

    except:
        pass

    return tree


class GitoliteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gitolite'

    def ready(self):
        repo = git_init()

        # Check if DB is up-to-date with gitolite
        logger.warn("Checking gitolite configuration")
        # Iterate keydir for users
        missing_users = []

        #userkeydirectories = os.listdir(os.path.join(settings.GITOLITE_ADMIN_PATH, 'keydir'))
        #for f in userkeydirectories:
        #    if not os.path.isdir(f) or User.objects.filter(username=f).exists():
        #        continue

        #    logger.warn("Adding user %s from gitolite keydir" % f)

        #    newuser = User(username=f)
        #    newuser.save()

        #    for k in os.listdir(os.path.join(settings.GITOLITE_ADMIN_PATH, 'keydir', f)):
        #        if os.path.isdir(k):
        #            continue
        #        keyfile = open(k, 'r')
        #        publickeydata = keyfile.read()

        #        newkey = RSA_Key(public=publickeydata, name=k, user=newuser)
        #        newkey.save()

        #logger.warn("Updating database")
        #logger.warn("Updating gitolite")

        # Serialize config:
        # @services = tonic
        # repo @all
        #   R = @services
        #
        # repo gitolite-admin
        #   RW = @services
        #   RW+ = admin
        #
        # include "groups.conf"
        # include "users/*"
