import os

from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.db.models import Count
from django.views.generic import ListView
from users.models import User

import paramiko

from gitolite.models import Repository, Collaborator

def index(request):
    context = {}

    if request.user.is_authenticated:
        context['repositories'] = request.user.repos.union(
            Repository.objects.filter(collabs__user=request.user)
        ).order_by('date_last_updated', 'date_created', 'name')[:8]
        context['invites'] = request.user.collabs.filter(accepted=False)

    return render(request, 'index/index.html', context=context)


def test(request):
    context = {}


    return HttpResponse("raw?", content_type='text/plain; charset=utf-8')


class UserView(ListView):
    model = User
    template_name = "index/user.html"
    context_object_name = 'user'


class RepositoryListView(ListView):
    model = Repository
    template_name = "index/discover.html"
    context_object_name = 'repositories'

    def get_context_data(self, **kwargs):
        context = super(RepositoryListView, self).get_context_data(**kwargs)
        context['num_repo'] = Repository.objects.count()
        context['user'] = User.objects.filter(is_superuser=False)
        context['num_user'] = context['user'].prefetch_related('keys').annotate(key_count=Count('keys')).filter(key_count__gt=0).count()
        context['num_collab'] = Collaborator.active.count()
        context['num_collab_rw'] = Collaborator.active.filter(perm__gte=Collaborator.Permissions.WRITE).count()
        return context
