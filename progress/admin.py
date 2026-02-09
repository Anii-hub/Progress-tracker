from django.contrib import admin
from .models import DailyProgress
from .models import Question, Contest
from .models import Badge, UserBadge
admin.site.register(DailyProgress)
admin.site.register(Question)
admin.site.register(Contest)
admin.site.register(Badge)
admin.site.register(UserBadge)
