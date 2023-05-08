from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.forms import ModelChoiceField
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

from users.models import User
from .models import Repository, Collaborator
from .forms import Collaborator_form
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


@method_decorator(ratelimit(key='header:x-real-ip', rate='2/h', method='POST', block=True), name='post')
class RepositoryCreate(LoginRequiredMixin, CreateView):
    model = Repository
    fields = ['owner', 'name', 'description', 'visibility']
    template_name = "gitolite/new.html"
    #context_object_name = 'repository'


    #def __init__(self, *args, **kwargs):
    #    super(RepositoryCreate, self).__init__(*args, **kwargs)

    #    self.fields['owner'].queryset = User.objects.filter(id=self.request.user.id)

# Returns the repository if the user has access to its settings
def user_has_settings_access(owner, reponame, user):
    # For "security by obscurity" reasons we need to return the same 404
    # message whether the user does not have permissions to view the repo,
    # or the repo simply does not exist
    exception404message = "Repository not found."

    repo = get_object_or_404_ext(Repository, exception404message, owner=owner, name=reponame)

    if user == owner:
        return repo

    collab = Collaborator.objects.filter(repo=repo, user=user)
    # if private && !collab = 404
    # if collab: repo
    # else permissiondenied
    if repo.visibility == Repository.Visibility.PRIVATE and collab.count() == 0:
        raise Http404(exception404message)
    if collab.count() > 1:
        raise Exception('Confused, collaborator query return more than 1 result.')

    collab = collab.first()

    if collab.perm == Collaborator.Permissions.READWRITEPLUS:
        return repo

    raise PermissionDenied('You do not have permissions to edit the settings of this repository.')


class RepositorySettings(LoginRequiredMixin, UpdateView):
    model = Repository
    template_name = "gitolite/repository_edit.html"
    context_object_name = 'repository'

    fields = ['name', 'visibility', 'description', 'default_branch']
    def get_object(self):
        owner = get_object_or_404(User, username=self.kwargs['owner'])
        reponame = self.kwargs['name']

        return user_has_settings_access(owner, reponame, self.request.user)

        raise PermissionDenied('You do not have permissions to edit the settings of this repository.')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['collaborators'] = Collaborator.objects.filter(repo=self.object)
        return context


@login_required
def RepositorySettingsCollab(request, owner, name):
    owner = get_object_or_404(User, username=owner)
    user = request.user
    repo = user_has_settings_access(owner, name, user)

    collabs = Collaborator.objects.filter(repo=repo)

    addform = Collaborator_form(initial={
        'repo': repo.id,
        'perm': Collaborator.Permissions.READ,
    })

    context = {
        'repository': repo,
        'collaborators': collabs,
        'addform': addform,
    }
    return render(request, 'gitolite/repository_edit_collabs.html', context=context)


@login_required
def AddCollaborator(request, owner, name):
    owner = get_object_or_404(User, username=owner)
    user = request.user
    repo = user_has_settings_access(owner, name, user)

    post = request.POST.copy()
    post['repo'] = repo.id
    post['user'] = get_object_or_404(User, username=post['username'])
    form = Collaborator_form(post)

    if form.is_valid():
        form.save()
    else:
        return HttpResponseRedirect(
                reverse('gitolite:repo-settings-collabs',
                        kwargs={'owner':owner.username, 'name': name},
                        context={'error': form.errors}))

    return HttpResponseRedirect(reverse('gitolite:repo-settings-collabs',
                                        kwargs={'owner':owner.username,
                                                'name': name}))


@login_required
def RemoveCollaborator(request, owner, name):
    owner = get_object_or_404(User, username=owner)
    user = request.user
    repo = user_has_settings_access(owner, name, user)

    post = request.POST.copy()

    args = {'owner':owner.username, 'name': name}

    for k,v in post.dict().items():
        if v == 'Remove':
            collab = get_object_or_404(Collaborator, repo=repo, id=k)
            collab.delete()
            return HttpResponseRedirect(reverse('gitolite:repo-settings-collabs',
                                        kwargs=args))

    return HttpResponseRedirect(reverse('gitolite:repo-settings-collabs'), context={'error':"Key not found"}, kwargs=args)

