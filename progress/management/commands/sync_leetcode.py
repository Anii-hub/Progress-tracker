from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import date

from accounts.leetcode import fetch_leetcode_stats
from progress.models import LeetCodeStats


class Command(BaseCommand):
    help = "Sync LeetCode stats for all users"

    def handle(self, *args, **kwargs):
        users = User.objects.all()

        for user in users:
            username = user.profile.leetcode_username

            if not username:
                continue

            stats = fetch_leetcode_stats(username)

            if not stats:
                continue

            LeetCodeStats.objects.update_or_create(
                user=user,
                date=date.today(),
                defaults={
                    "total_solved": stats["total"],
                    "easy": stats["easy"],
                    "medium": stats["medium"],
                    "hard": stats["hard"],
                }
            )

            self.stdout.write(self.style.SUCCESS(f"Synced {user.username}"))

        self.stdout.write(self.style.SUCCESS("Sync complete!"))
