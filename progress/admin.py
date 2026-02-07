from django.contrib import admin
from .models import DailyProgress
from .models import Question, Contest
admin.site.register(DailyProgress)
admin.site.register(Question)
admin.site.register(Contest)
