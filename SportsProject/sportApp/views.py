from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import SpacePost, SpaceComment, GameScore, ScoreComment, DirectMessage , FriendRequest, Friendship , Profile
from googleapiclient.discovery import build
from django.db.models import Q
from datetime import datetime, timedelta, timezone, date
from dotenv import load_dotenv
import requests, os, html
load_dotenv()


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

def clips(request):
    api_key = os.getenv('YOUTUBE_API_KEY')

    time_threshold = datetime.now(timezone.utc) - timedelta(hours=48)
    published_after = time_threshold.strftime('%Y-%m-%dT%H:%M:%SZ')

    NBA_CHANNEL_ID = "UCWJ2lWNubArHWmf3FIHbfcQ"

    youtube = build('youtube', 'v3', developerKey=api_key)

    params = {
        'part': 'snippet',
        'q': 'NBA highlights -shorts',
        'key': api_key,
        'maxResults': 30,
        'type': 'video',
        'videoEmbeddable': 'true',
        'publishedAfter': published_after,
        'order': 'viewCount',
    }

    response = requests.get('https://www.googleapis.com/youtube/v3/search', params=params)
    results = response.json().get('items', [])

    videos = []
    for item in results:
        channel_id = item['snippet']['channelId']

        if channel_id == NBA_CHANNEL_ID:
            continue

        videos.append({
            'title': html.unescape(item['snippet']['title']),
            'id': item['id']['videoId'],
            'thumbnail': item['snippet']['thumbnails']['high']['url'],
        })

        if len(videos) >= 8:
            break

    return render(request, 'clips.html', {'videos': videos})

def search(request):
    query = request.GET.get("q", "")

    posts = SpacePost.objects.filter(
        Q(title__icontains=query) |
        Q(message__icontains=query) |
        Q(user__username__icontains=query)
    ).distinct()

    users = User.objects.filter(username__icontains=query)

    return render(request, "search.html", {
        "query": query,
        "posts": posts,
        "users": users
    })


def profile(request):
    if not request.user.is_authenticated:
        return redirect("login")
    API_KEY = "apikeygoeshere"
    BASE_URL = "https://api.balldontlie.io/v1"
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)
 
    response = requests.get(
        f"{BASE_URL}/teams",
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    teams = []
    if response.ok:
        try:
            teams = response.json().get("data", [])
        except Exception:
            teams = []

    if request.method == "POST":

        # username
        name = request.POST.get("name")
        if name:
            user.username = name
            user.save()

        # bio
        profile.bio = request.POST.get("bio", "")

        # favorite team
        profile.favorite_team = request.POST.get("favorite_team", "")

        # profile picture
        if request.FILES.get("profile_picture"):
            profile.profile_picture = request.FILES["profile_picture"]

        profile.save()
        return redirect("profile")
 
    return render(request, "profile.html", {
        "profile": profile,
        "teams": teams
    })

 
 
def add_friends(request):
    if not request.user.is_authenticated:
        return redirect("login")

    # send friend request
    if request.method == "POST" and "friend_username" in request.POST:
        username = request.POST.get("friend_username")
        try:
            target_user = User.objects.get(username=username)
            if target_user != request.user:
                already_sent = FriendRequest.objects.filter(
                    from_user=request.user,
                    to_user=target_user
                ).exists()
                if not already_sent:
                    FriendRequest.objects.create(
                        from_user=request.user,
                        to_user=target_user
                    )
        except User.DoesNotExist:
            pass

    # accept request
    if request.method == "POST" and "accept_request" in request.POST:
        request_id = request.POST.get("accept_request")
        friend_request = FriendRequest.objects.get(
            id=request_id,
            to_user=request.user
        )
        friendship = Friendship.objects.create()
        friendship.users.add(request.user)
        friendship.users.add(friend_request.from_user)
        friend_request.delete()

    # decline request
    if request.method == "POST" and "decline_request" in request.POST:
        request_id = request.POST.get("decline_request")
        friend_request = FriendRequest.objects.get(
            id=request_id,
            to_user=request.user
        )

        friend_request.delete()

    # get friends
    friendships = Friendship.objects.filter(users=request.user)
    friends = []
    for friendship in friendships:
        for user in friendship.users.all():
            if user != request.user:
                friends.append(user)
    # get incoming requests
    friend_requests = FriendRequest.objects.filter(to_user=request.user)

    return render(request, "add_friends.html", {
        "friends": friends,
        "friend_requests": friend_requests
    })