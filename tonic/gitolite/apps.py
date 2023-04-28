from django.conf import settings
from django.apps import AppConfig
#from django.contrib.auth import get_user_model
from git import Repo
#from users.models import RSA_Key
import logging
import paramiko
import os

#User = get_user_model()
logger = logging.getLogger(__name__)



def init_git():
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


class GitoliteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gitolite'

    def ready(self):
        repo = init_git()

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
