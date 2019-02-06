from django.shortcuts import render
from django.http import HttpResponse

import paramiko

def index(request):
    context = {}
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.connect('localhost', 22, 'git', '', key_filename="/home/oscar/.ssh/id_rsa")
    _, stdout, stderr = ssh.exec_command('info')

    res = stdout.readlines()
    if len(stderr.readlines()):
        context.update({'git_error': "<br>".join(stderr.readlines())})
    else:
        context.update({'git_response': "<br>".join(stdout.readlines())})
    ssh.close()

    res = '\n'.join(res)
    # Remove welcome message
    res = filter(lambda x: len(x) > 0,res[res.find('\n'):].split('\n'))
    # Remove CREATOR-line
    res = filter(lambda r:"CREATOR" not in r, res)
    # Seperate into (permission, reponame/description)
    res = list(map(lambda r: tuple((r.split('\t'))), list(res)))
    # filter permission
    (permissions, repositories) = list(zip(*res))
    permissions = map(lambda p: p.replace(' ', ''), permissions)
    repositories = map(lambda r: r.split('/') if '/' in r else ['', r], repositories)

    context.update({
        'git_response': list(zip(permissions,repositories))
    })

    return render(request, 'index/index.html', context=context)
