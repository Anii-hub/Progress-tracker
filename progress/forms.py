from django import forms
from .models import DailyProgress

class DailyProgressForm(forms.ModelForm):
    class Meta:
        model = DailyProgress
        fields = ['problems_solved']

