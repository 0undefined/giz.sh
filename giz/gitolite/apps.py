from django.apps import AppConfig
from django.conf import settings
from django.db import transaction
from django.http import Http404
from git import Repo, Tree, Blob
from umarkdown import markdown

import logging
import paramiko
import os


logger = logging.getLogger(__name__)


# TODO:
# Add a management command to update DB from gitolite-admin

@transaction.atomic(durable=False)
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
        return Repo(gitolite_admin_dir)
    else:
        logger.warn("Cloning gitolite-admin to " + gitolite_admin_dir)
        # Clone the repo otherwise
        repo = Repo.clone_from(
            'git@' + settings.GITOLITE_HOST + ':gitolite-admin.git',
            to_path=gitolite_admin_dir
        )

        # Check if gitolite has needed configuration
        userdir = os.path.join(gitolite_admin_dir, 'conf', 'users')
        organizationdir = os.path.join(gitolite_admin_dir, 'conf', 'orgs')
        gitoliteconf_path = os.path.join(gitolite_admin_dir, 'conf', 'gitolite.conf')

        if not (os.path.exists(userdir) and os.path.isdir(userdir)):
            os.makedirs(userdir)

        if not (os.path.exists(organizationdir) and os.path.isdir(organizationdir)):
            os.makedirs(organizationdir)

        # Check if they are included
        gitoliteconf = open(gitoliteconf_path , 'r')
        conf_lines = gitoliteconf.readlines()

        includes_userconf = False
        includes_orgconf = False

        for line in conf_lines:
            # Remove empty strings from split(' ')
            cmd = filter(lambda x: len(x) > 0, line.split(' '))
            if len(cmd) == 2 and cmd[0] == "include":
                if cmd[1].find('users/*'):  # We dont really care if they use the correct suffix
                    if includes_userconf:
                        gitoliteconf.close()
                        raise Exception("Already found some sort of user inclusion!")

                    includes_userconf = True

                if cmd[1].find('orgs/*'):
                    if includes_orgconf:
                        gitoliteconf.close()
                        raise Exception("Already found some sort of organization inclusion!")

                    includes_orgconf = True

            if includes_userconf and includes_orgconf:
                break

        gitoliteconf.close()

        if not (includes_userconf and includes_orgconf):
            # Append the missing option(s)
            gitoliteconf = open(gitoliteconf_path , 'a')

            if not includes_userconf:
                gitoliteconf.write('\ninclude "users/*.conf"\n')

            if not includes_orgconf:
                gitoliteconf.write('\ninclude "orgs/*.conf"\n')

            gitoliteconf.close()


    return repo


@transaction.atomic(durable=True)
def git_add_key_file(key):
    from django.contrib.auth import get_user_model
    from users.models import RSA_Key
    User = get_user_model()

    if not isinstance(key, RSA_Key):
        raise TypeError("Expected RSA_Key object in first argument, got %s" % (str(type(key))))

    keyname_dir = os.path.join(settings.GITOLITE_ADMIN_PATH, 'keydir', key.name)
    repo = git_init()

    if not os.path.exists(keyname_dir):
        os.makedirs(keyname_dir)

    user = key.user

    keypath = os.path.join(keyname_dir, user.username + '.pub')
    keyfile = open(keypath, 'w')
    keyfile.write(key.public)
    keyfile.close()

    # Commit it to gitolite
    repo.index.add([keypath])
    repo.index.commit("Add user %s's ssh key \"%s.pub\"" % (user.username, key.name))
    # TODO: Handle error?
    repo.remote().push().raise_if_error()


@transaction.atomic(durable=True)
def git_rm_key_file(key):
    from django.contrib.auth import get_user_model
    from users.models import RSA_Key
    User = get_user_model()

    if not isinstance(key, RSA_Key):
        raise TypeError("Expected RSA_Key object in first argument, got %s" % (str(type(key))))

    keyname_dir = os.path.join(settings.GITOLITE_ADMIN_PATH, 'keydir', key.name)
    repo = git_init()

    user = key.user

    keypath = os.path.join(keyname_dir, user.username + '.pub')

    if not os.path.exists(keypath):
        return

    # Commit it to gitolite
    repo.index.remove([keypath], working_tree=True)
    #repo.index.add([keypath])
    repo.index.commit("Remove user %s's ssh key \"%s.pub\"" % (user.username, key.name))
    if os.path.exists(keypath):
        raise Exception("You don goof again")
    # TODO: Handle error?
    repo.remote().push().raise_if_error()
    repo.close()


@transaction.atomic(durable=True)
def git_update_userrepos(user):
    from django.contrib.auth import get_user_model
    from .models import Repository
    User = get_user_model()

    if not isinstance(user, User):
        raise TypeError("Expected User object in first argument, got %s" % (str(type(user))))

    userconfpath = os.path.join(settings.GITOLITE_ADMIN_PATH, 'conf', 'users', user.username + '.conf')
    repo = git_init()

    userrepos = Repository.objects.filter(owner=user)
    userconf = open(userconfpath, 'w')
    userconf.write('\n\n'.join([repo.get_config() for repo in userrepos]) + '\n')
    userconf.close()

    # Commit it to gitolite
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

    # No need to call `git_init`, since we retrieve the info from the RO mount
    # it's always up-to-date since it is updated directly from the gitolite
    # service
    repo_path = repo.get_absolute_path()
    filecontent = ""

    try:
        repo = Repo(repo_path)
        filecontent = repo.git.show('{}:{}'.format(repo.active_branch.name, filename))

    except:
        pass

    return filecontent


def git_get_readme_html(repo):
    return markdown(git_get_file_content(repo, "README.md")
                    , unsafe=False
                    , no_breaks=True)


def convert_list(t):
    if len(t.trees) == 1 and len(t.blobs) == 0:
        deep_list = convert_list(t.trees[0])
        if isinstance(deep_list, Tree) or isinstance(deep_list, Blob):
            # Run at end of recursion
            return {'path': t.name + '/' + deep_list.name, 'object': deep_list}
        else:
            # Run when recursing
            return {'path': t.name + '/' + deep_list['path'], 'object': deep_list['object']}

    elif len(t.blobs) == 1 and len(t.trees) == 0:
        return t.blobs[0]
    else:
        return t

def git_get_tree(repo, subdir=None):
    from .models import Repository

    if not isinstance(repo, Repository):
        raise TypeError("Expected Repository object in first argument, got %s" % (str(type(repo))))

    # Same reason to not call `git_init` as in `git_get_file_content`
    repo_path = repo.get_absolute_path()
    tree = {'files': [], 'dirs': []}

    try:
        repository = Repo(repo_path)
        tree_ = repository.tree()

        subdirs = []
        files = []

        if isinstance(subdir, str):
            subdirs = subdir.split('/')
            subdirs.reverse()

            while len(subdirs) > 0:
                d = subdirs.pop()
                dd = list(filter(lambda t: t.name == d, tree_.trees))

                if len(dd) != 1:
                    raise Http404("Could not find file or directory in tree")

                tree_ = dd[0]

        tree['files'] = tree_.blobs
        tree['dirs'] = [convert_list(t) for t in tree_.trees]

    except Exception as e:
        logger.warn("Failed to get tree for %s -- %s" % (repo.name, e))
        return tree

    return tree


class GitoliteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gitolite'

# TODO: make a git_update_db_from_config
# Reads the configuration in gitolite-admin.git and updates the DB accordingly.
# Can lead to potentially password-less users.
