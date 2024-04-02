from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
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
from .forms import (
    Collaborator_form,
    RepositoryForm,
    IssueForm,
    RepositoryDocumentationGenerationForm,
    RepositoryReleaseGenerationForm,
    IssueCommentForm,
    RepositoryBranchPermForm,
)
from .apps import git_get_readme_html, git_get_tree


# TODO:
# Create some base classes for viewing and accessing settings respectively.
# Each of the views in this source file can benefit from it, so that I don't
# need to write `get_context` for every bloody view.
# Also get_object is getting kinda tedious.

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

    #owner = get_object_or_404_ext(User, exception404message, username=owner)
    repo = get_object_or_404_ext(Repository, exception404message, owner__username=owner, name=name)

    if repo.visibility == Repository.Visibility.PUBLIC:
        return repo

    if not user.is_authenticated:
        raise Http404(exception404message)

    if user.username == owner:
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

    #owner = get_object_or_404_ext(User, exception404message, username=owner)

    if user.username == owner:
        return repo

    # If the user has repo read perms, it is okay to return permission denied.
    collab = Collaborator.active.filter(repo=repo, user=user)

    if collab.count() > 1:
        raise Exception('Confused, collaborator query returned more than 1 result.')

    collab = collab.first()

    if collab.perm == Collaborator.Permissions.READWRITEPLUS:
        return repo

    raise PermissionDenied('You do not have permissions to edit the settings of this repository.')


def get_repository_tabs(repository : Repository):
    ret = []

    if repository.issue_permission != Repository.PermissionChoices.DISABLED:
        ret.append({'name': "issues", 'icon': "fa-circle-dot", 'displayname': "Issues",
                    'url': reverse('gitolite:issue_list', kwargs={'owner':repository.owner.username, 'name': repository.name})})

    if repository.pullrequest_permission != Repository.PermissionChoices.DISABLED:
        ret.append({'name': "pulls",  'icon': "fa-code-pull-request", 'displayname': "Pull requests"})

    if repository.docs_generation != Repository.DocumentationGeneration.DISABLED:
        ret.append({'name': "docs", 'icon': "fa-book", 'displayname': "Documentation"})

    if repository.release_generation != Repository.ReleaseGeneration.DISABLED:
        ret.append({'name': "releases", 'icon': "fa-cube", 'displayname': "Releases"})

    if repository.analytics != Repository.AnalyticsOptions.DISABLED:
        ret.append({'name': "anal", 'icon': "fa-chart-line", 'displayname': "Analytics"})

    if len(ret) > 0:
        ret.insert(0, {'name': "code", 'icon': "fa-code", 'displayname': "Code",
                       'url': repository.get_absolute_url()})

    return ret


def query_string(query: str, repo=None):
    # is:open
    #   matches either status that is open, ie. open and reopened.
    # is:closed
    #   matches any status that is closed, ie. closed, wontfix, and duplicate.
    # status:<STATUS>
    #   matches all issues with status=<STATUS>
    # @<usrname>
    #   matches all issues where @username occurs
    # author:username
    #   matches all issues that @username authored

    #return Issue.objects.filter(repo=repo)
    query = query.split()
    queryset = Issue.objects.all()

    if not repo is None:
        queryset.filter(repo=repo)

    #raise Exception(queryset.all())

    queryset.prefetch_related('issuecomments')

    if len(query) == 0:
        return queryset

    filters = []

    for term in query:
        tt = term.split(':', maxsplit=1)

        if len(tt) == 1:
            filters.append(
                       queryset.filter(message__contains=tt[0])
                     | queryset.filter(title__contains=tt[0])
                     | queryset.filter(issuecomments__message__contains=tt[0])
                     )


        elif tt[0] == "is":
            if tt[1] == "open":
                filters.append(
                           queryset.filter(status=Issue.IssueStatusOptions.OPEN)
                         | queryset.filter(status=Issue.IssueStatusOptions.REOPENED)
                         )

            elif tt[1] == "closed":
                filters.append(
                           queryset.filter(status=Issue.IssueStatusOptions.CLOSED)
                         | queryset.filter(status=Issue.IssueStatusOptions.WONTFIX)
                         | queryset.filter(status=Issue.IssueStatusOptions.DUPLICATE)
                         )


        elif tt[0] == "status":
            t = tt[1].lower().strip()
            status = 0

            try:
                status = list(filter(lambda s: s.name.lower() == t, list(Issue.IssueStatusOptions)))[0]
            except:
                raise Exception("Invalid status '{}'".format(t))

            filters.append(queryset.filter(status=status))


        elif tt[0] == "author":
            filters.append(queryset.filter(author__username=tt[1]))


    for f in filters:
        queryset = queryset.intersection(f)

    return queryset


class RepositoryView(DetailView):
    model = Repository
    template_name = "gitolite/repository.html"
    context_object_name = 'repository'

    def get_object(self):
        return view_repo(self.request.user, self.kwargs['owner'], self.kwargs['name'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tabs'] = get_repository_tabs(self.object)
        context['collaborators'] = self.object.collabs.filter(accepted=True).prefetch_related('user').annotate(count=Count('user')) #Collaborator.active.filter(repo=self.object)
        context['active'] = "code"

        if self.request.user.is_authenticated:
            context['collaborators_pending'] = self.object.collabs.filter(accepted=False, user=self.request.user)

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


class RepositorySettingsBase(LoginRequiredMixin):
    def get_object(self):
        return user_has_settings_access(self.request.user, self.kwargs['owner'], self.kwargs['name'])


class RepositorySettings(RepositorySettingsBase, UpdateView):
    model = Repository
    template_name = "gitolite/repository_edit.html"
    context_object_name = 'repository'

    fields = ['name', 'visibility', 'description', 'default_branch']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['collaborators'] = Collaborator.objects.filter(repo=self.object)
        return context


class RepositorySettingsDocumentation(RepositorySettingsBase, UpdateView):
    form_class = RepositoryDocumentationGenerationForm
    template_name = "gitolite/repository_edit_documentation.html"
    context_object_name = 'repository'


class RepositorySettingsReleases(RepositorySettingsBase, UpdateView):
    form_class = RepositoryReleaseGenerationForm
    template_name = "gitolite/repository_edit_releases.html"
    context_object_name = 'repository'


# TODO: Fix this mess (merge with updateview)
@login_required
def RepositorySettingsCollab(request, owner, name):
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
    paginate_by = 10
    model = Issue
    context_object_name = 'issues'

    DEFAULT_QUERY = 'is:open'

    # TODO:
    # Limit issues to repo-lreated ones.
    def get_queryset(self):
        # Check if theres a search term or something
        #raise Exception(self.request.GET.copy())
        repo = view_repo(self.request.user, self.kwargs['owner'], self.kwargs['name'])

        get = self.request.GET.copy()
        search_term = get.pop('search', ['is:open'])[0]

        queryset = query_string(search_term, repo=repo)
        # TODO: Sorting from GET params
        queryset = queryset.order_by('-date_updated')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        get = self.request.GET.copy()
        search_term = get.pop('search', [None])[0]

        context['repository'] = view_repo(self.request.user, self.kwargs['owner'], self.kwargs['name'])
        context['active'] = "issues"
        context['tabs'] = get_repository_tabs(context['repository'])
        context['search_term'] = 'is:open' if search_term is None else search_term
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
        context['tabs'] = get_repository_tabs(context['repository'])
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.repo = view_repo(self.request.user, self.kwargs['owner'], self.kwargs['name'])
        return super(IssueCreate, self).form_valid(form)


@method_decorator(ratelimit(key='header:x-real-ip', rate='30/h', method='POST', block=True), name='post')
class IssueView(CreateView):
    form_class = IssueCommentForm
    #model = Issue
    template_name = "gitolite/issue_detail.html"
    #context_object_name = 'issue'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['repository'] = view_repo(self.request.user, self.kwargs['owner'], self.kwargs['name'])
        context['collaborators'] = Collaborator.active.filter(repo=context['repository'])
        context['active'] = "issues"
        context['tabs'] = get_repository_tabs(context['repository'])

        repo = view_repo(self.request.user, self.kwargs['owner'], self.kwargs['name'])
        context['issue'] = get_object_or_404(Issue, repo=repo, issueid=self.kwargs['issueid'])

        return context


    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("You do not have the privileges to perform this action")

        # Check permissions for logged in user
        form.instance.author = self.request.user
        repo = view_repo(self.request.user, self.kwargs['owner'], self.kwargs['name'])

        form.instance.issue = get_object_or_404(Issue, repo=repo, issueid=self.kwargs['issueid'])

        return super(IssueView, self).form_valid(form)


@method_decorator(ratelimit(key='header:x-real-ip', rate='30/h', method='POST', block=True), name='post')
class BranchPermissionView(RepositorySettingsBase, UpdateView):
    form_class = RepositoryBranchPermForm
    template_name = "gitolite/repository_edit_branches.html"
    context_object_name = 'repository'

    def get_queryset(self):
        return []
