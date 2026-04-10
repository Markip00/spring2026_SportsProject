from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        confirm = request.POST['confirm_password']

        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('signup')

        user = User.objects.create_user(username=username, password=password)
        user.save()
        return redirect('login')

    return render(request, 'signup.html')


def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid login")
            return redirect('login')

    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('login')

def home(request):
    return render(request, 'home.html', {})

def watchparty(request):
    return render(request, 'watchparty.html', {})

def spaces(request):
    return render(request, 'spaces.html', {})

def clips(request):
    return render(request, 'clips.html', {})

def news(request):
    return render(request, 'news.html',{})

def edit_profile(request):
    return render(request, 'edit_profile.html',{})

def add_friends(request):
    return render(request, 'add_friends.html',{})


def direct_messages(request):
    return render(request, 'direct_messages.html', {})

def premium(request):
    return render(request, 'premium.html',{})


