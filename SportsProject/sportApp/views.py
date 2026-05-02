from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SpacePost, SpaceComment
from googleapiclient.discovery import build

from datetime import date
import requests

@login_required
def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']  
        password = request.POST['password']
        confirm = request.POST['confirm_password']

        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('signup')

        user = User.objects.create_user(
            username=username,
            email=email,      
            password=password
        )

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
 
def spaces(request):
    if request.method == "POST":
        action = request.POST.get("action")

        if not request.user.is_authenticated:
            return redirect("login")

        if action == "new_post":
            title = request.POST.get("title")
            message = request.POST.get("message")

            if title and message:
                SpacePost.objects.create(
                    user=request.user,
                    title=title,
                    message=message
                )

        elif action == "comment":
            post_id = request.POST.get("post_id")
            comment = request.POST.get("comment")
            post = get_object_or_404(SpacePost, id=post_id)

            if comment:
                SpaceComment.objects.create(
                    post=post,
                    user=request.user,
                    comment=comment
                )

        elif action == "like":
            post_id = request.POST.get("post_id")
            post = get_object_or_404(SpacePost, id=post_id)

            if request.user in post.likes.all():
                post.likes.remove(request.user)
            else:
                post.likes.add(request.user)

        return redirect("spaces")

    posts = SpacePost.objects.all().order_by("-created_at")
    return render(request, "spaces.html", {"posts": posts})

def clips(request):
    return render(request, 'clips.html', {})

def scores(request): 
    API_KEY = "apikey_goes_here" 
    BASE_URL = "https://api.balldontlie.io"

    headers = {"Authorization": API_KEY}
    today = date.today().isoformat()
    today_display = date.today().strftime("%m/%d/%Y")
    response = requests.get(
        f"{BASE_URL}/nba/v1/games",
        headers=headers,
        params={"dates[]": today}
    )

    games = []

    if response.status_code == 200:
        data = response.json()
        for game in data.get("data", []):
            games.append({
                "home": game["home_team"]["full_name"],
                "away": game["visitor_team"]["full_name"],
                "score": f"{game['visitor_team_score']}-{game['home_team_score']}",
                "status": game["status"]
            })
 
    return render(request, "scores.html", {
        "games": games,
        "date": today_display
    })

def edit_profile(request):
    return render(request, 'edit_profile.html',{})

def add_friends(request):
    return render(request, 'add_friends.html',{})


def direct_messages(request):
    return render(request, 'direct_messages.html', {})

def premium(request):
    return render(request, 'premium.html',{})

def youtube_search(query):
    youtube = build('youtube', 'v3', developerKey='your_key_here')

    request = youtube.search().list(
        q=query,
        part='snippet',
        type='video',     # video, channel, playlist
        maxResults=10,    # max results pulled
        order='relevance' # date, relevance, viewcount, etc
        # publishedAfter: 2026-01-01T00:00:00Z ## finds clips from last 24 hours or curr week
    )

    response = request.execute()

    for item in response.get('items', []):
        title = item['snippet']['title']
        video_id = item['id']['videoId']
        print(f"Title: {title} | ID: {video_id}")


def clips_page(request):
    api_key = 'YOUTUBE_API_KEY'
    search_url = 'https://www.googleapis.com/youtube/v3/search'

    params = {
        'part': 'snippet',
        'q': 'Trending NBA highlights',
        'key': api_key,
        'maxResults': 12,
        'type': 'video',
        'order': 'date',
    }

    response = requests.get(search_url, params=params)
    results = response.json().get('items', [])

    videos = []
    for item in results:
        videos.append({
            'title': item['snippet']['title'],
            'id': item['id']['videoId'],
            'thumbnail': item['snippet']['thumbnails']['high']['url'],
        })

    return render(request, 'clips.html', {'videos': videos})


