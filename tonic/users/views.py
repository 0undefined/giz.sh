import re

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from . import forms
User = get_user_model()


def Users(request):
    context = {'users': User.objects.all()}
    return render(request, 'users/index.html', context=context)


def UserView(request, user=None):
    userobj = get_object_or_404(User, username=user)
    context = {'user': userobj,}
            # Associates/friends
    return render(request, 'users/profile.html', context=context)


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
