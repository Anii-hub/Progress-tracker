from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from accounts.views import signup
from django.contrib.auth import views as auth_views
from progress.views import add_progress
from progress.views import progress_list
from progress.views import start_session, end_session
from accounts.views import edit_profile
from accounts.views import leetcode_stats
from progress.views import weekly_stats
from accounts.views import (
    send_friend_request,
    accept_friend_request,
    friends_list
)


def home(request):
    return render(request, 'home.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('signup/', signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('progress/', add_progress, name='add_progress'),
    path('my-progress/', progress_list, name='progress_list'),
    path('start-session/', start_session, name='start_session'),
    path('end-session/', end_session, name='end_session'),
    path('profile/', edit_profile, name='edit_profile'),
    path('leetcode/', leetcode_stats, name='leetcode_stats'),
    path('weekly/', weekly_stats, name='weekly_stats'),
    path('friends/', friends_list, name='friends_list'),
    path('friend-request/send/<int:user_id>/', send_friend_request, name='send_friend_request'),
    path('friend-request/accept/<int:request_id>/', accept_friend_request, name='accept_friend_request'),


]
