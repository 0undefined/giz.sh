from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from django.forms import ModelChoiceField

from users.models import User
from .models import Repository, Collaborator


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

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["visibility"] = Repository.Visibility.choices[self.object.visibility][1]
        context["collaborators"] = Collaborator.objects.filter(repo=self.object)
        return context


class RepositoryCreate(LoginRequiredMixin, CreateView):
    model = Repository
    fields = ['owner', 'name', 'description', 'visibility']
    template_name = "git/new.html"
    #context_object_name = 'repository'


    #def __init__(self, *args, **kwargs):
    #    super(RepositoryCreate, self).__init__(*args, **kwargs)

    #    self.fields['owner'].queryset = User.objects.filter(id=self.request.user.id)
