from django import forms
from .models import DailyProgress
from .models import Duel,Contest
class DailyProgressForm(forms.ModelForm):
    class Meta:
        model = DailyProgress
        fields = ['problems_solved']

from django import forms
from django.contrib.auth.models import User


# =========================
# DUEL FORM (CUSTOM FORM)
# =========================
class DuelForm(forms.Form):
    opponent = forms.ModelChoiceField(
        queryset=User.objects.none(),
        widget=forms.Select(attrs={"class": "form-control"})
    )

    duration = forms.IntegerField(
        label="Duration (minutes)",
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "30"
        })
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # show only friends in dropdown
        from accounts.models import FriendRequest

        sent = FriendRequest.objects.filter(
            sender=user, is_accepted=True
        ).values_list("receiver_id", flat=True)

        received = FriendRequest.objects.filter(
            receiver=user, is_accepted=True
        ).values_list("sender_id", flat=True)

        friend_ids = list(sent) + list(received)

        self.fields["opponent"].queryset = User.objects.filter(id__in=friend_ids)


# =========================
# CONTEST FORM (CUSTOM FORM)
# =========================
class ContestForm(forms.Form):
    title = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Weekly DSA Contest"
        })
    )

    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            "type": "datetime-local",
            "class": "form-control"
        })
    )

    duration = forms.IntegerField(
        label="Duration (minutes)",
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "60"
        })
    )
