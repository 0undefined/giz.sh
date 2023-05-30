from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.forms import ModelChoiceField
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

from users.models import User
from .models import Repository, Collaborator, Issue, Repository
from .forms import Collaborator_form, RepositoryForm, IssueForm
from .apps import git_get_readme_html, git_get_tree

def get_object_or_404_ext(model, message, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        raise Http404(message)


# Raises 404 instead of permission denied
def view_repo(user : User, owner : str, name : str):
    # For "security by obscurity" reasons we need to return the same 404
    # message whether the user does not have permissions to view the repo,
    # or the repo simply does not exist
    exception404message = "Repository not found"

    owner = get_object_or_404_ext(User, exception404message, username=owner)
    repo = get_object_or_404_ext(Repository, exception404message, owner=owner, name=name)

    if repo.visibility == Repository.Visibility.PUBLIC:
        return repo

    if not user.is_authenticated:
        raise Http404(exception404message)

    if user == owner:
        return repo

    # We allow users that has been invited to view some of the repo before
    # deciding to accept it.
    get_object_or_404_ext(Collaborator, exception404message, repo=repo, user=user)

    # Return repo if implicit test is passed above
    return repo


# Returns the repository if the user has access to its settings
def user_has_settings_access(user : User, owner : str, reponame : str):
    exception404message = "Repository not found"

    # This results in a _lot_ of duplicate requests, but it is more readable
    # (imo) and more "stable" in terms of changes.
    repo = view_repo(user, owner, reponame)

    owner = get_object_or_404_ext(User, exception404message, username=owner)

    if user == owner:
        return repo

    # If the user has repo read perms, it is okay to return permission denied.
    collab = Collaborator.active.filter(repo=repo, user=user)

    if collab.count() > 1:
        raise Exception('Confused, collaborator query returned more than 1 result.')

    collab = collab.first()

    if collab.perm == Collaborator.Permissions.READWRITEPLUS:
        return repo

    raise PermissionDenied('You do not have permissions to edit the settings of this repository.')


class RepositoryView(DetailView):
    model = Repository
    template_name = "gitolite/repository.html"
    context_object_name = 'repository'

    def get_object(self):
        return view_repo(self.request.user, self.kwargs['owner'], self.kwargs['name'])

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['collaborators'] = Collaborator.active.filter(repo=self.object)
        context['active'] = "code"
        if self.request.user.is_authenticated:
            context['collaborators_pending'] = Collaborator.objects.filter(repo=self.object, accepted=False, user=self.request.user)
        # Extend to /owner/repo/(blob|tree)/branch/filename url path (for files/dirs)
        # Extend to /owner/repo/(blob|tree)/branch url path (for branches)
        # Reminder: blob=file tree=dir
        context['readme'] = git_get_readme_html(self.object)
        context['tree'] = git_get_tree(self.object)
        return context


@method_decorator(ratelimit(key='header:x-real-ip', rate='2/h', method='POST', block=True), name='post')
class RepositoryCreate(LoginRequiredMixin, CreateView):
    form_class = RepositoryForm
    template_name = "gitolite/new.html"

    def get_form_kwargs(self):
        kwargs = super(RepositoryCreate, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs



class RepositorySettings(LoginRequiredMixin, UpdateView):
    model = Repository
    template_name = "gitolite/repository_edit.html"
    context_object_name = 'repository'

    fields = ['name', 'visibility', 'description', 'default_branch']

    def get_object(self):
        return user_has_settings_access(self.request.user, self.kwargs['owner'], self.kwargs['name'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['collaborators'] = Collaborator.objects.filter(repo=self.object)
        return context


@login_required
def RepositorySettingsCollab(request, owner, name):
    #owner = get_object_or_404(User, username=owner)
    user = request.user
    repo = user_has_settings_access(user, owner, name)

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
@ratelimit(key='header:x-real-ip', rate='30/h', method='POST', block=True)
def AddCollaborator(request, owner, name):
    #owner = get_object_or_404(User, username=owner)
    user = request.user
    repo = user_has_settings_access(user, owner, name)

    post = request.POST.copy()
    post['repo'] = repo.id
    post['user'] = get_object_or_404(User, username=post['username'])
    form = Collaborator_form(post)

    if form.is_valid():
        form.save()
    else:
        return HttpResponseRedirect(
            reverse('gitolite:repo-settings-collabs', kwargs={'owner':repo.owner.username, 'name': name})
        )  #context={'error': form.errors}

    return HttpResponseRedirect(
        reverse('gitolite:repo-settings-collabs', kwargs={'owner':repo.owner.username, 'name': name})
    )


@login_required
def RemoveCollaborator(request, owner, name):
    #owner = get_object_or_404(User, username=owner)
    user = request.user
    repo = user_has_settings_access(user, owner, name)

    post = request.POST.copy()

    args = {'owner':owner.username, 'name': name}

    for k,v in post.dict().items():
        if v == 'Remove':
            collab = get_object_or_404(Collaborator, repo=repo, id=k)
            collab.delete()
            return HttpResponseRedirect(
                reverse('gitolite:repo-settings-collabs', kwargs={'owner':repo.owner.username, 'name': name})
            )

    # todo: return a "Error key not found"
    return HttpResponseRedirect(
        reverse('gitolite:repo-settings-collabs', kwargs={'owner':repo.owner.username, 'name': name})
    )


@login_required
def CollabResponse(request):
    if request.method != 'POST':
        return HttpResponseRedirect(reverse('index'))

    post = request.POST.copy()
    user = request.user
    raise Exception(post)

    return HttpResponseRedirect(repo.get_absolute_url())


class IssueListView(ListView):
    model = Issue
    context_object_name = 'issues'

    # TODO:
    # Limit issues to repo-lreated ones.
    def get_queryset(self):
        repo = view_repo(self.request.user, self.kwargs['owner'], self.kwargs['name'])

        queryset = Issue.objects.filter(repo=repo)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['repository'] = view_repo(self.request.user, self.kwargs['owner'], self.kwargs['name'])
        context['active'] = "issues"
        return context


@method_decorator(ratelimit(key='header:x-real-ip', rate='30/h', method='POST', block=True), name='post')
class IssueCreate(LoginRequiredMixin, CreateView):
    form_class = IssueForm
    template_name = "gitolite/issue_form.html"

    def get_form_kwargs(self):
        kwargs = super(IssueCreate, self).get_form_kwargs()
        kwargs['author'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['repository'] = view_repo(self.request.user, self.kwargs['owner'], self.kwargs['name'])
        context['collaborators'] = Collaborator.active.filter(repo=context['repository'])
        context['active'] = "issues"
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.repo = view_repo(self.request.user, self.kwargs['owner'], self.kwargs['name'])
        return super(IssueCreate, self).form_valid(form)



class IssueView(DetailView):
    model = Issue
    #template_name = "gitolite/.html"
    context_object_name = 'issue'

    def get_object(self):
        repo = view_repo(self.request.user, self.kwargs['owner'], self.kwargs['name'])
        return get_object_or_404(Issue, repo=repo, issueid=self.kwargs['issueid'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['repository'] = view_repo(self.request.user, self.kwargs['owner'], self.kwargs['name'])
        context['collaborators'] = Collaborator.active.filter(repo=context['repository'])
        context['active'] = "issues"
        return context
