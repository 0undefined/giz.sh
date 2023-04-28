import re

from django.contrib.auth import get_user_model, authenticate, login, logout
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse

from .models import RSA_Key
from .forms import RSA_KeyForm
from . import forms
User = get_user_model()

from gitolite.models import Repository


def Users(request):
    context = {'users': User.objects.all()}
    return render(request, 'users/index.html', context=context)


def UserView(request, user=None):
    userobj = get_object_or_404(User, username=user)
    context = {'user': userobj, 'repositories': Repository.objects.filter(owner=userobj)}
            # Associates/friends
    return render(request, 'users/user.html', context=context)


def EditUser(request, user=None):
    userobj = get_object_or_404(User, username=user)
    if userobj.username == request.user.username:
        form_rsa = RSA_KeyForm()
        context = {'user': userobj, 'keys': RSA_Key.objects.filter(user=userobj), 'form_rsa': form_rsa}
                # Associates/friends
        return render(request, 'users/edit.html', context=context)
    # TODO: return permission denied
    return render(request, 'index/index.html')


def AddUserKey(request, user=None):
    userobj = get_object_or_404(User, username=user)
    form = RSA_KeyForm(request.POST.copy() or None)
    form.data['user'] = userobj

    if (form.is_valid()):
        form.save()
    else:
        return JsonResponse(form.errors)

    return HttpResponseRedirect(reverse('users:edit', kwargs={'user':user}))


def Userlogin(request):
    context = {}
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            context.update({
                'error': "Login failed",
            })
    return render(request, 'users/login.html')


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
            if re.match(r'[\w-]+$', form.data['username']) is not None:
                username = form.data['username']
                password = form.data['password']
                User.objects.create_user(username=username, password=password)
                return HttpResponseRedirect('/')
            else:
                context.update({'error': "Invalid username. Please stick to alphanumeric characters"})
        else:
            context.update({
                'error': "Validation failed",
                'errors': form.errors
            })
    return render(request, 'users/signup.html', context=context)
