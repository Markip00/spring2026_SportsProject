from django.shortcuts import render, redirect

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

def sign_up(request):
    return render(request, 'sign_up.html',{})

def log_in(request):
    return render(request, 'log_in.html',{})



