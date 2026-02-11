from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q

from .forms import ProfileForm
from .leetcode import fetch_leetcode_stats
from .models import FriendRequest, Notification


# 🔔 Notification helper
def create_notification(user, message):
    Notification.objects.create(user=user, message=message)


# ---------------- SIGNUP ----------------

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'accounts/signup.html', {'form': form})


# ---------------- EDIT PROFILE ----------------

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


# ---------------- LEETCODE STATS ----------------

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


# ---------------- SEND FRIEND REQUEST ----------------

@login_required
def send_friend_request(request, user_id):
    receiver = User.objects.get(id=user_id)

    if receiver != request.user:
        FriendRequest.objects.get_or_create(
            sender=request.user,
            receiver=receiver
        )

        # 🔔 Notify receiver
        create_notification(
            receiver,
            f"{request.user.username} sent you a friend request"
        )

    return redirect('friends_page')


# ---------------- ACCEPT FRIEND REQUEST ----------------

@login_required
def accept_friend_request(request, request_id):
    friend_request = FriendRequest.objects.get(
        id=request_id,
        receiver=request.user
    )
    friend_request.is_accepted = True
    friend_request.save()

    # 🔔 Notify sender
    create_notification(
        friend_request.sender,
        f"{request.user.username} accepted your friend request"
    )

    return redirect('friends_page')


# ---------------- FRIENDS PAGE ----------------

@login_required
def friends_page(request):
    query = request.GET.get('q')

    users = User.objects.exclude(id=request.user.id)

    # Search users
    if query:
        users = users.filter(username__icontains=query)

    # Accepted friends
    sent = FriendRequest.objects.filter(
        sender=request.user, is_accepted=True
    ).values_list('receiver_id', flat=True)

    received = FriendRequest.objects.filter(
        receiver=request.user, is_accepted=True
    ).values_list('sender_id', flat=True)

    friends_ids = list(sent) + list(received)

    # Pending sent requests
    sent_requests = FriendRequest.objects.filter(
        sender=request.user, is_accepted=False
    ).values_list('receiver_id', flat=True)

    # Incoming requests
    received_requests = FriendRequest.objects.filter(
        receiver=request.user, is_accepted=False
    )

    friends = User.objects.filter(id__in=friends_ids)

    return render(request, 'accounts/friends.html', {
        'users': users,
        'friends': friends,
        'friends_ids': friends_ids,
        'sent_requests': sent_requests,
        'received_requests': received_requests,
    })


# ---------------- NOTIFICATIONS PAGE ----------------

@login_required
def notifications(request):
    notes = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/notifications.html', {'notes': notes})
def landing(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'landing.html')
