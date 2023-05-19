import re

from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic.edit import UpdateView
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator


from .models import RSA_Key, Invitation, Organization, UserFollower
from .forms import RSA_KeyForm
from . import forms
User = get_user_model()

from gitolite.models import Repository, Collaborator


def Users(request):
    context = {'users': User.objects.all()}
    return render(request, 'users/index.html', context=context)


class UserView(DetailView):
    model = User
    template_name = "users/profile.html"
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super(UserView, self).get_context_data(**kwargs)
        repos = (
            # Get both own repos and collab repos
            Repository.objects.filter(owner=self.object) | Repository.objects.filter(collabs__user=self.object)
        # TODO: Filter out unaccepted collabs
        ).prefetch_related('collabs').annotate(collab_count=Count('collabs'))

        # If this is not the owner, show only public & collaboration repos
        if self.request.user != self.object:
            repos = repos.filter(
                visibility=Repository.Visibility.PUBLIC
            ).union(
                repos.filter(
                    visibility=Repository.Visibility.PRIVATE,
                    collabs__user=self.request.user
                )
            )

        organizations = Organization.objects.filter(members__user=self.object)

        context['repositories'] = repos.order_by('date_created')
        context['organizations'] = organizations

        follows = UserFollower.objects.filter(following=self.object) | UserFollower.objects.filter(follower=self.object)

        context['followers'] = follows.filter(following=self.object).count()
        context['following'] = follows.filter(follower=self.object).count()
        context['is_following'] = follows.filter(follower=self.request.user).count() > 0
        return context

    def get_object(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return user


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['name', 'bio', 'email']
    def get_object(self):
        return get_object_or_404(User, username=self.request.user.username)


@login_required
def UserInvitationsView(request):
    userobj = get_object_or_404(User, id=request.user.id)
    if userobj.username == request.user.username:
        referer = None
        try:
            referer = Invitation.objects.get(user=userobj)
        except Invitation.DoesNotExist:
            pass

        context = {'user': userobj, 'invitations': Invitation.objects.filter(referer=userobj), 'referer': referer}
        return render(request, 'users/user_invitations.html', context=context)
    return PermissionDenied("You do not have authorization to view or edit this page")


@login_required
def EditUserKeys(request):
    userobj = get_object_or_404(User, id=request.user.id)
    if userobj.username == request.user.username:
        form_rsa = RSA_KeyForm()
        context = {'user': userobj, 'keys': RSA_Key.objects.filter(user=userobj), 'form_rsa': form_rsa}
        return render(request, 'users/keys.html', context=context)
    return PermissionDenied("You do not have authorization to view or edit this page")


@login_required
def AddUserKey(request):
    userobj = get_object_or_404(User, id=request.user.id)
    form = RSA_KeyForm(request.POST.copy() or None)
    form.data['user'] = userobj

    if (form.is_valid()):
        form.save()
    else:
        return JsonResponse(form.errors)

    return HttpResponseRedirect(reverse('users:settings-keys'))


@login_required
def RmUserKey(request):
    userobj = get_object_or_404(User, id=request.user.id)
    post = request.POST.copy()

    #return PermissionDenied(post.decode())

    for k,v in post.dict().items():
        ## TODO: Allow people to create ssh-keys named 'csrfmiddlewaretoken'
        #if k == 'csrfmiddlewaretoken':
        #    continue

        if v == 'Remove':
            key = get_object_or_404(RSA_Key, user_id=request.user.id, name=k)
            key.delete()
            return HttpResponseRedirect(reverse('users:settings-keys'))

    return HttpResponseRedirect(reverse('users:settings-keys'), context={'error':"Key not found"})


@method_decorator(ratelimit(key='header:x-real-ip', rate='5/h', method='POST', block=True), name='post')
class UserLogin(LoginView):
    template_name = 'users/login.html'


def Userlogout(request):
    logout(request)
    return HttpResponseRedirect('/')


@ratelimit(key='header:x-real-ip', rate='15/h', method='POST', block=True)
def Signup(request):
    context = {
        'signupform': forms.SignupForm
    }
    if request.method == 'GET':
        return render(request, 'users/signup.html', context=context)
    elif request.method == 'POST':
        form = forms.SignupForm(request.POST)
        if form.is_valid():
            form.save()  #User.objects.create_user(username=username, password=password)
            return HttpResponseRedirect('/')
        else:
            context.update({
                #'error': "Validation failed",
                #'errors': form.errors,
                'form': form,
            })
    return render(request, 'users/signup.html', context=context)


@login_required
def CollabResponse(request):
    if request.method != 'POST':
        return HttpResponseRedirect(reverse('index'))

    userobj = get_object_or_404(User, id=request.user.id)
    post = request.POST.copy()
    collab_id = int(post.get('collab_id'))

    collab = get_object_or_404(Collaborator, id=collab_id)
    repo = collab.repo

    accept = False
    decline = False

    for label,value in post.dict().items():
        if label == 'accept' or value == 'accept':
            accept = True
        if label == 'decline' or value == 'decline':
            decline = True

    if accept == decline:
        raise Exception("that does not make any sense")

    if accept:
        collab.accept()

        return HttpResponseRedirect(repo.get_absolute_url())
    else:
        collab.delete()

    return HttpResponseRedirect(reverse('index'))


@login_required
def Follow(request):
    if request.method != 'POST':
        return HttpResponseRedirect(reverse('index'))

    follower = get_object_or_404(User, id=request.user.id)
    post = request.POST.copy()

    following = get_object_or_404(User, username=post.get('user', None))

    if post.get('follow', False):
        f = UserFollower(follower=follower, following=following)
        f.save()
    else:
        f = get_object_or_404(UserFollower, follower=follower, following=following)
        f.delete()

    #raise Exception({'ff': f, 'post':post})

    return HttpResponseRedirect(following.get_absolute_url())
