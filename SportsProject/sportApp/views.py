from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SpacePost, SpaceComment, GameScore, ScoreComment, DirectMessage
from django.db.models import Q

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
    API_KEY = "00ba9f97-a38b-42c7-b1f6-9db22f17d68a" 
    BASE_URL = "https://api.balldontlie.io"

    today = date.today().isoformat()
    today_display = date.today().strftime("%m/%d/%Y")

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")

        game_id = request.POST.get("game_id")
        comment = request.POST.get("comment")

        game = get_object_or_404(GameScore, id=game_id)

        if comment:
            ScoreComment.objects.create(
                game=game,
                user=request.user,
                comment=comment
            )

        return redirect("scores")

    headers = {"Authorization": API_KEY}

    response = requests.get(
        f"{BASE_URL}/nba/v1/games",
        headers=headers,
        params={"dates[]": today}
    )

    if response.status_code == 200:
        data = response.json()

        for game in data.get("data", []):
            GameScore.objects.update_or_create(
                game_id=str(game["id"]),
                defaults={
                    "home_team": game["home_team"]["full_name"],
                    "away_team": game["visitor_team"]["full_name"],
                    "home_score": game["home_team_score"],
                    "away_score": game["visitor_team_score"],
                    "status": game["status"],
                    "game_date": today,
                }
            )

    games = GameScore.objects.filter(game_date=today).order_by("id")

    return render(request, "scores.html", {
        "games": games,
        "date": today_display
    })

def edit_profile(request):
    return render(request, 'edit_profile.html',{})

def add_friends(request):
    return render(request, 'add_friends.html',{})


@login_required
def direct_messages(request):
    users = User.objects.exclude(id=request.user.id)

    return render(request, "direct_messages.html", {
        "users": users
    })


@login_required
def dm_chat(request, username):
    other_user = get_object_or_404(User, username=username)

    if request.method == "POST":
        message = request.POST.get("message")

        if message:
            DirectMessage.objects.create(
                sender=request.user,
                receiver=other_user,
                message=message
            )

        return redirect("dm_chat", username=other_user.username)

    messages = DirectMessage.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by("created_at")

    return render(request, "dm_chat.html", {
        "other_user": other_user,
        "messages": messages
    })

def premium(request):
    return render(request, 'premium.html',{})


