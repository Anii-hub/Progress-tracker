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
from .models import Contest
from .forms import ContestForm
from datetime import date, timedelta
from .models import Question
from .models import Duel
from .forms import DuelForm


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
            update_streak(request.user)
            check_badges(request.user)



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
@login_required
def create_contest(request):
    if request.method == 'POST':
        form = ContestForm(request.POST, user=request.user)
        if form.is_valid():
            opponent = form.cleaned_data['opponent']

            start = date.today()
            end = start + timedelta(days=7)

            Contest.objects.create(
                creator=request.user,
                opponent=opponent,
                start_date=start,
                end_date=end
            )

            return redirect('home')
    else:
        form = ContestForm(user=request.user)

    return render(request, 'progress/create_contest.html', {'form': form})

from .models import Contest

@login_required
def my_contests(request):
    today = timezone.now().date()

    contests = Contest.objects.filter(
        start_date__lte=today,
        end_date__gte=today
    ).filter(
        creator=request.user
    ) | Contest.objects.filter(
        opponent=request.user,
        start_date__lte=today,
        end_date__gte=today
    )

    return render(request, 'progress/my_contests.html', {
        'contests': contests
    })
@login_required
def question_bank(request):
    topic = request.GET.get('topic')
    difficulty = request.GET.get('difficulty')

    questions = Question.objects.all()

    if topic:
        questions = questions.filter(topic__icontains=topic)

    if difficulty:
        questions = questions.filter(difficulty=difficulty)

    return render(request, 'progress/question_bank.html', {
        'questions': questions
    })
@login_required
def start_duel(request):
    if request.method == 'POST':
        form = DuelForm(request.POST, user=request.user)
        if form.is_valid():
            opponent = form.cleaned_data['opponent']
            duration = int(form.cleaned_data['duration'])
            difficulty = form.cleaned_data['difficulty']

            start_time = timezone.now()
            end_time = start_time + timedelta(minutes=duration)

            # fetch leetcode stats safely
            my_stats = fetch_leetcode_stats(request.user.profile.leetcode_username)
            opp_stats = fetch_leetcode_stats(opponent.profile.leetcode_username)

            my_total = my_stats["total"] if my_stats else 0
            opp_total = opp_stats["total"] if opp_stats else 0

            Duel.objects.create(
                creator=request.user,
                opponent=opponent,
                start_time=start_time,
                end_time=end_time,
                difficulty=difficulty,
                creator_start_solved=my_total,
                opponent_start_solved=opp_total
            )

            return redirect('active_duels')
    else:
        form = DuelForm(user=request.user)

    return render(request, 'progress/start_duel.html', {'form': form})

@login_required
def active_duels(request):
    finish_duels()

    now = timezone.now()

    duels = Duel.objects.filter(
        creator=request.user
    ) | Duel.objects.filter(
        opponent=request.user
    )

    active = duels.filter(is_finished=False)
    finished = duels.filter(is_finished=True)

    questions = Question.objects.all()[:3]

    return render(request, 'progress/active_duels.html', {
        'active_duels': active,
        'finished_duels': finished,
        'questions': questions
    })

def finish_duels():
    now = timezone.now()
    duels = Duel.objects.filter(is_finished=False, end_time__lte=now)

    for duel in duels:
        creator_stats = fetch_leetcode_stats(duel.creator.profile.leetcode_username)
        opponent_stats = fetch_leetcode_stats(duel.opponent.profile.leetcode_username)

        creator_end = creator_stats["total"] if creator_stats else 0
        opponent_end = opponent_stats["total"] if opponent_stats else 0

        duel.creator_end_solved = creator_end
        duel.opponent_end_solved = opponent_end

        creator_gain = creator_end - duel.creator_start_solved
        opponent_gain = opponent_end - duel.opponent_start_solved

        if creator_gain > opponent_gain:
            duel.winner = duel.creator.username
        elif opponent_gain > creator_gain:
            duel.winner = duel.opponent.username
        else:
            duel.winner = "Draw"

        duel.is_finished = True
        duel.save()
def update_streak(user):
    today = date.today()
    yesterday = today - timedelta(days=1)

    today_progress = DailyProgress.objects.filter(user=user, date=today).exists()
    yesterday_progress = DailyProgress.objects.filter(user=user, date=yesterday).exists()

    profile = user.profile

    if today_progress:
        if yesterday_progress:
            profile.current_streak += 1
        else:
            profile.current_streak = 1

        if profile.current_streak > profile.longest_streak:
            profile.longest_streak = profile.current_streak

        profile.save()
from django.db.models import Sum
from .models import Badge, UserBadge, DailyProgress, Duel

def check_badges(user):

    def give_badge(badge_name, description):
        badge, created = Badge.objects.get_or_create(
            name=badge_name,
            defaults={"description": description}
        )

        if not UserBadge.objects.filter(user=user, badge=badge).exists():
            UserBadge.objects.create(user=user, badge=badge)

    # First progress badge
    if DailyProgress.objects.filter(user=user).count() >= 1:
        give_badge("First Progress", "Added first progress entry")

    # Streak badges
    if user.profile.current_streak >= 3:
        give_badge("3 Day Streak", "Maintained 3 day streak")

    if user.profile.current_streak >= 7:
        give_badge("7 Day Streak", "Maintained 7 day streak")

    # Problems solved badge
    total_problems = DailyProgress.objects.filter(user=user)\
        .aggregate(Sum('problems_solved'))['problems_solved__sum'] or 0

    if total_problems >= 10:
        give_badge("10 Problems", "Solved 10 problems")

    # Duel win badge
    if Duel.objects.filter(winner=user.username).exists():
        give_badge("First Duel Win", "Won first duel")
