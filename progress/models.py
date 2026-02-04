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
