from django.contrib import admin
from .models import TimerRecord, WeeklyReset


@admin.register(TimerRecord)
class TimerRecordAdmin(admin.ModelAdmin):
    list_display  = ['user', 'activity', 'duration_seconds', 'week_id', 'started_at']
    list_filter   = ['activity', 'week_id']
    search_fields = ['user__username']
    ordering      = ['-started_at']


@admin.register(WeeklyReset)
class WeeklyResetAdmin(admin.ModelAdmin):
    list_display  = ['user', 'week_id', 'score', 'streak_achieved', 'streak_count_after', 'reset_at']
    list_filter   = ['streak_achieved']
    search_fields = ['user__username']
    ordering      = ['-week_id']
