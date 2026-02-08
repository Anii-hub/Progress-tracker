from django import forms
from .models import DailyProgress

class DailyProgressForm(forms.ModelForm):
    class Meta:
        model = DailyProgress
        fields = ['problems_solved']

from django.contrib.auth.models import User

class ContestForm(forms.Form):
    opponent = forms.ModelChoiceField(queryset=User.objects.none())

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        # show only friends as opponents
        from accounts.models import FriendRequest

        sent = FriendRequest.objects.filter(
            sender=user, is_accepted=True
        ).values_list('receiver_id', flat=True)

        received = FriendRequest.objects.filter(
            receiver=user, is_accepted=True
        ).values_list('sender_id', flat=True)

        friend_ids = list(sent) + list(received)

        self.fields['opponent'].queryset = User.objects.filter(id__in=friend_ids)

class DuelForm(forms.Form):
    opponent = forms.ModelChoiceField(queryset=User.objects.none())
    duration = forms.ChoiceField(choices=[
        (30, '30 minutes'),
        (45, '45 minutes'),
        (60, '60 minutes'),
    ])
    difficulty = forms.ChoiceField(choices=[
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ])

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        from accounts.models import FriendRequest

        sent = FriendRequest.objects.filter(sender=user, is_accepted=True)\
            .values_list('receiver_id', flat=True)
        received = FriendRequest.objects.filter(receiver=user, is_accepted=True)\
            .values_list('sender_id', flat=True)

        friend_ids = list(sent) + list(received)
        self.fields['opponent'].queryset = User.objects.filter(id__in=friend_ids)
