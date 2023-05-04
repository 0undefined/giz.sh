from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from django.forms import ModelChoiceField
from django.http import Http404

from users.models import User
from .models import Repository, Collaborator
from .apps import git_get_readme_html, git_get_tree

def get_object_or_404_ext(model, message, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        raise Http404(message)


class RepositoryView(DetailView):
    model = Repository
    template_name = "gitolite/repository.html"
    context_object_name = 'repository'

    def get_object(self):
        owner = get_object_or_404(User, username=self.kwargs['owner'])
        reponame = self.kwargs['name']

        # For "security by obscurity" reasons we need to return the same 404
        # message whether the user does not have permissions to view the repo,
        # or the repo simply does not exist
        exception404message = "Repository not found"

        repo = get_object_or_404_ext(Repository, exception404message, owner=owner, name=self.kwargs['name'])

        if repo.visibility == Repository.Visibility.PUBLIC:
            return repo

        user = self.request.user
        if user == owner:
            return repo

        get_object_or_404_ext(Collaborator, exception404message, repo=repo, user=user)

        return repo

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
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
