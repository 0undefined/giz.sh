from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from users.models import User
from .models import Repository


class RepositoryView(DetailView):
    model = Repository
    template_name = "git/repository.html"
    context_object_name = 'repository'

    def get_object(self):
        user = get_object_or_404(User, username=self.kwargs['owner'])
        return get_object_or_404(
            Repository,
            owner_id=user.id,
            name=self.kwargs['name'],
        )
