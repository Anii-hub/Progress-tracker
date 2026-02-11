from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class DailyProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    problems_solved = models.PositiveIntegerField(default=0)
    study_hours = models.DecimalField(max_digits=4, decimal_places=1, default=0)


    class Meta:
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.username} - {self.date}"


class StudySession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.duration_minutes} min"
class Contest(models.Model):
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='created_contests'
    )
    opponent = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='opponent_contests'
    )

    start_date = models.DateField()
    end_date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.creator} vs {self.opponent}"
class Question(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]

    title = models.CharField(max_length=200)
    topic = models.CharField(max_length=100)
    company = models.CharField(max_length=100, blank=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    link = models.URLField()

    def __str__(self):
        return f"{self.title} ({self.difficulty})"
class Duel(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='duels_created')
    opponent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='duels_received')

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    difficulty = models.CharField(max_length=10)

    creator_start_solved = models.IntegerField(default=0)
    opponent_start_solved = models.IntegerField(default=0)

    creator_end_solved = models.IntegerField(null=True, blank=True)
    opponent_end_solved = models.IntegerField(null=True, blank=True)

    winner = models.CharField(max_length=50, null=True, blank=True)

    is_finished = models.BooleanField(default=False)

    def __str__(self):
        return f"Duel: {self.creator} vs {self.opponent}"

# ------------------- BADGES -------------------

class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"
class LeetCodeStats(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()

    total_solved = models.IntegerField()
    easy = models.IntegerField()
    medium = models.IntegerField()
    hard = models.IntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.date}"
