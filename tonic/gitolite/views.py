from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from django.forms import ModelChoiceField

from users.models import User
from .models import Repository, Collaborator
from .apps import git_get_readme_html, git_get_tree


class RepositoryView(DetailView):
    model = Repository
    template_name = "gitolite/repository.html"
    context_object_name = 'repository'

    def get_object(self):
        user = get_object_or_404(User, username=self.kwargs['owner'])
        reponame = self.kwargs['name']
        return Repository.objects.get(owner_id=user.id, name=self.kwargs['name'])
        #get_object_or_404(
        #    Repository,
        #    owner_id=user.id,
        #    name=self.kwargs['name']
        #)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['visibility'] = Repository.Visibility.choices[self.object.visibility][1]
        context['collaborators'] = Collaborator.objects.filter(repo=self.object)
        # Extend to /owner/repo/(blob|tree)/branch/filename url path (for files/dirs)
        # Extend to /owner/repo/(blob|tree)/branch url path (for branches)
        # Reminder: blob=file tree=dir
        context['readme'] = git_get_readme_html(self.object)
        context['files'] = git_get_tree(self.object)
        return context


class RepositoryCreate(LoginRequiredMixin, CreateView):
    model = Repository
    fields = ['owner', 'name', 'description', 'visibility']
    template_name = "gitolite/new.html"
    #context_object_name = 'repository'


    #def __init__(self, *args, **kwargs):
    #    super(RepositoryCreate, self).__init__(*args, **kwargs)

    #    self.fields['owner'].queryset = User.objects.filter(id=self.request.user.id)
