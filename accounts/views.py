from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm
from .leetcode import fetch_leetcode_stats
from django.contrib.auth.models import User
from .models import FriendRequest


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'accounts/edit_profile.html', {'form': form})
@login_required
def leetcode_stats(request):
    profile = request.user.profile
    stats = None

    if profile.leetcode_username:
        stats = fetch_leetcode_stats(profile.leetcode_username)

    return render(request, 'accounts/leetcode_stats.html', {
        'stats': stats,
        'username': profile.leetcode_username
    })
@login_required
def send_friend_request(request, user_id):
    receiver = User.objects.get(id=user_id)

    if receiver != request.user:
        FriendRequest.objects.get_or_create(
            sender=request.user,
            receiver=receiver
        )

    return redirect('home')
@login_required
def accept_friend_request(request, request_id):
    friend_request = FriendRequest.objects.get(
        id=request_id,
        receiver=request.user
    )
    friend_request.is_accepted = True
    friend_request.save()

    return redirect('home')
@login_required
def friends_list(request):
    sent = FriendRequest.objects.filter(
        sender=request.user,
        is_accepted=True
    )
    received = FriendRequest.objects.filter(
        receiver=request.user,
        is_accepted=True
    )

    friends = [f.receiver for f in sent] + [f.sender for f in received]

    return render(request, 'accounts/friends.html', {
        'friends': friends
    })
