import re

from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic.edit import UpdateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import RSA_Key, Invitation
from .forms import RSA_KeyForm
from . import forms
User = get_user_model()

from gitolite.models import Repository


def Users(request):
    context = {'users': User.objects.all()}
    return render(request, 'users/index.html', context=context)


class UserView(DetailView):
    model = User
    template_name = "users/profile.html"
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super(UserView, self).get_context_data(**kwargs)
        context['repositories'] = Repository.objects.filter(owner=self.object)
        return context

    def get_object(self):
        user = get_object_or_404(User, id=self.request.user.id)
        # TODO: prefetch related repos
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
    # TODO: return permission denied
    return PermissionDenied("You do not have authorization to view or edit this page")


@login_required
def EditUserKeys(request):
    userobj = get_object_or_404(User, id=request.user.id)
    if userobj.username == request.user.username:
        form_rsa = RSA_KeyForm()
        context = {'user': userobj, 'keys': RSA_Key.objects.filter(user=userobj), 'form_rsa': form_rsa}
        return render(request, 'users/keys.html', context=context)
    # TODO: return permission denied
    return PermissionDenied("You do not have authorization to view or edit this page")


def AddUserKey(request):
    userobj = get_object_or_404(User, id=request.user.id)
    form = RSA_KeyForm(request.POST.copy() or None)
    form.data['user'] = userobj

    if (form.is_valid()):
        form.save()
    else:
        return JsonResponse(form.errors)

    return HttpResponseRedirect(reverse('users:settings-keys'))


class UserLogin(LoginView):
    template_name = 'users/login.html'


def Userlogout(request):
    logout(request)
    return HttpResponseRedirect('/')


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
