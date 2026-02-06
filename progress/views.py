from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta, date
from .models import DailyProgress, StudySession
from .forms import DailyProgressForm
from accounts.leetcode import fetch_leetcode_stats
from django.db.models import Sum
from datetime import date, timedelta
from .models import DailyProgress
from accounts.models import FriendRequest

@login_required
def add_progress(request):
    today = date.today()
    user = request.user
    profile = user.profile

    progress, created = DailyProgress.objects.get_or_create(
        user=user,
        date=today
    )

    # ---------------- STUDY HOURS (DAY 7) ----------------
    total_minutes = StudySession.objects.filter(
        user=user,
        start_time__date=today
    ).aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0

    progress.study_hours = round(total_minutes / 60, 2)

    # ---------------- PROBLEMS SOLVED (DAY 10) ----------------
    if profile.leetcode_username:
        stats = fetch_leetcode_stats(profile.leetcode_username)

        if stats:
            today_total = stats['total']
            solved_today = today_total - profile.last_leetcode_total

            if solved_today < 0:
                solved_today = 0  # safety check

            progress.problems_solved = solved_today

            # update profile for next sync
            profile.last_leetcode_total = today_total
            profile.save()

    if request.method == 'POST':
        form = DailyProgressForm(request.POST, instance=progress)
        if form.is_valid():
            form.save()
            return redirect('progress_list')
    else:
        form = DailyProgressForm(instance=progress)

    return render(request, 'progress/add_progress.html', {
        'form': form,
        'progress': progress
    })



@login_required
def progress_list(request):
    progress_entries = DailyProgress.objects.filter(
        user=request.user
    ).order_by('-date')

    # -------- STREAK LOGIC --------
    streak = 0
    today = timezone.now().date()

    for entry in progress_entries:
        if entry.date == today - timedelta(days=streak):
            streak += 1
        else:
            break

    # -------- SESSION SUMMARY (DAY 6) --------
    total_minutes = StudySession.objects.filter(
        user=request.user,
        start_time__date=today
    ).aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0

    total_hours = round(total_minutes / 60, 2)

    return render(request, 'progress/progress_list.html', {
        'progress_entries': progress_entries,
        'streak': streak,
        'total_hours': total_hours,
    })


from django.http import HttpResponse
@login_required
def start_session(request):
    StudySession.objects.create(
        user=request.user,
        start_time=timezone.now()
    )
    return redirect('home')
@login_required
def end_session(request):
    session = StudySession.objects.filter(
        user=request.user,
        end_time__isnull=True
    ).last()

    if session:
        session.end_time = timezone.now()
        duration = session.end_time - session.start_time
        session.duration_minutes = int(duration.total_seconds() / 60)
        session.save()

    return redirect('home')
@login_required
def weekly_stats(request):
    today = date.today()
    week_start = today - timedelta(days=6)

    week_progress = DailyProgress.objects.filter(
        user=request.user,
        date__range=[week_start, today]
    ).order_by('date')

    dates = [p.date.strftime("%d %b") for p in week_progress]
    study_hours = [p.study_hours for p in week_progress]
    problems = [p.problems_solved for p in week_progress]

    total_hours = sum(study_hours)
    total_problems = sum(problems)

    days_count = len(week_progress) or 1
    avg_hours = round(total_hours / days_count, 2)
    avg_problems = round(total_problems / days_count, 2)

    return render(request, 'progress/weekly_stats.html', {
        'week_progress': week_progress,
        'dates': dates,
        'study_hours': study_hours,
        'problems': problems,
        'total_hours': total_hours,
        'total_problems': total_problems,
        'avg_hours': avg_hours,
        'avg_problems': avg_problems,
        'week_start': week_start,
        'today': today,
    })
def get_weekly_totals(user):
    today = date.today()
    week_start = today - timedelta(days=6)

    week_progress = DailyProgress.objects.filter(
        user=user,
        date__range=[week_start, today]
    )

    total_hours = sum(p.study_hours for p in week_progress)
    total_problems = sum(p.problems_solved for p in week_progress)

    return total_hours, total_problems
@login_required
def friends_progress(request):
    user = request.user

    # get friend ids
    sent = FriendRequest.objects.filter(
        sender=user, is_accepted=True
    ).values_list('receiver_id', flat=True)

    received = FriendRequest.objects.filter(
        receiver=user, is_accepted=True
    ).values_list('sender_id', flat=True)

    friend_ids = list(sent) + list(received)

    friends = User.objects.filter(id__in=friend_ids)

    comparison_data = []

    # current user stats
    my_hours, my_problems = get_weekly_totals(user)
    comparison_data.append({
        'name': "You",
        'hours': my_hours,
        'problems': my_problems
    })

    # friends stats
    for friend in friends:
        hours, problems = get_weekly_totals(friend)
        comparison_data.append({
            'name': friend.username,
            'hours': hours,
            'problems': problems
        })
    # sort by study hours (descending)
    comparison_data = sorted(
    comparison_data,
    key=lambda x: x['hours'],
    reverse=True
)

    names = [row['name'] for row in comparison_data]
    hours = [row['hours'] for row in comparison_data]
    problems = [row['problems'] for row in comparison_data]

    return render(request, 'progress/friends_progress.html', {
        'comparison_data': comparison_data,
        'names': names,
        'hours': hours,
        'problems': problems,
    })

