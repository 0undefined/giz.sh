import os

from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.views.generic import ListView
from users.models import User

import paramiko

from gitolite.models import Repository

def index(request):
    context = {}
    #ssh = paramiko.SSHClient()
    #ssh.load_system_host_keys()
    #ssh.connect(settings.GITOLITE_HOST, settings.GITOLITE_PORT, 'git', '', key_filename=settings.GITOLITE_KEY)
    #_, stdout, stderr = ssh.exec_command('info')

    #res = stdout.readlines()
    #if len(stderr.readlines()):
    #    context.update({'git_error': "<br>".join(stderr.readlines())})
    #else:
    #    context.update({'git_response': "<br>".join(stdout.readlines())})
    #ssh.close()

    #res = '\n'.join(res)
    ## Remove welcome message
    #res = filter(lambda x: len(x) > 0,res[res.find('\n'):].split('\n'))
    ## Remove CREATOR-line
    #res = filter(lambda r:"CREATOR" not in r, res)
    ## Seperate into (permission, reponame/description)
    #res = list(map(lambda r: tuple((r.split('\t'))), list(res)))
    ## filter permission
    #(permissions, repositories) = list(zip(*res))
    #permissions = map(lambda p: p.replace(' ', ''), permissions)
    #repositories = map(lambda r: r.split('/') if '/' in r else ['', r], repositories)

    #context.update({
    #    'git_response': list(zip(permissions,repositories))
    #})

    return render(request, 'index/index.html', context=context)


class UserView(ListView):
    model = User
    template_name = "index/user.html"
    context_object_name = 'user'


class RepositoryListView(ListView):
    model = Repository
    template_name = "index/discover.html"
    context_object_name = 'repositories'
