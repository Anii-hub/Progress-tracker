from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from accounts.models import FriendRequest


@login_required
def home(request):
    # Get all users except current user
    all_users = User.objects.exclude(id=request.user.id)

    # Friends where you sent request and accepted
    friends_sent = FriendRequest.objects.filter(
        sender=request.user,
        is_accepted=True
    ).values_list('receiver_id', flat=True)

    # Friends where you received request and accepted
    friends_received = FriendRequest.objects.filter(
        receiver=request.user,
        is_accepted=True
    ).values_list('sender_id', flat=True)

    friends_ids = list(friends_sent) + list(friends_received)

    # Requests you already sent but not accepted yet
    sent_requests = FriendRequest.objects.filter(
        sender=request.user,
        is_accepted=False
    ).values_list('receiver_id', flat=True)

    return render(request, 'home.html', {
        'users': all_users,
        'friends_ids': friends_ids,
        'sent_requests': sent_requests,
    })
