import paramiko

class Gitolite():
    sshkey = ''
    user = 'tonic'

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
