from django.shortcuts import render, redirect

def home(request):
    return render(request, 'home.html', {})

def News(request):
    return render(request, 'News.html',{})