from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from accounts import views
from accounts.views import signup
from django.contrib.auth import views as auth_views
from progress.views import active_duels, add_progress, start_duel, contest_list

from progress.views import progress_list
from progress.views import start_session, end_session
from accounts.views import edit_profile
from accounts.views import leetcode_stats
from progress.views import weekly_stats
from accounts.views import (
    send_friend_request,
    accept_friend_request,
    friends_page,notifications
)
from core.views import home
from progress.views import friends_progress
from progress.views import create_contest
from progress.views import my_contests
from progress.views import question_bank
from accounts.views import landing
from progress.views import badges 

urlpatterns = [
    path('admin/', admin.site.urls),
    

    path('', landing, name='landing'),
    path('home/', home, name='home'),
    path("badges/", badges, name="badges"),

    path('signup/', signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('progress/', add_progress, name='add_progress'),
    path('my-progress/', progress_list, name='progress_list'),
    path('start-session/', start_session, name='start_session'),
    path('end-session/', end_session, name='end_session'),
    path('profile/', edit_profile, name='edit_profile'),
    path('leetcode/', leetcode_stats, name='leetcode_stats'),
    path('weekly/', weekly_stats, name='weekly_stats'),
    path('friends/', friends_page, name='friends_page'),
    path('friend-request/send/<int:user_id>/', send_friend_request, name='send_friend_request'),
    path('friend-request/accept/<int:request_id>/', accept_friend_request, name='accept_friend_request'),
    path('friends-progress/', friends_progress, name='friends_progress'),
    path('create-contest/', create_contest, name='create_contest'),
    path("contests/", contest_list, name="contest_list"),
    path("my-contests/", my_contests, name="my_contests"),

    path('questions/', question_bank, name='question_bank'),
    path('start-duel/', start_duel, name='start_duel'),
    path('active-duels/', active_duels, name='active_duels'),
    path('notifications/', notifications, name='notifications'),







]
