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

    if request.user.is_authenticated:
        context['repositories'] = request.user.repos.all()
        context['invites'] = request.user.collabs.all()

    return render(request, 'index/index.html', context=context)


class UserView(ListView):
    model = User
    template_name = "index/user.html"
    context_object_name = 'user'


class RepositoryListView(ListView):
    model = Repository
    template_name = "index/discover.html"
    context_object_name = 'repositories'
