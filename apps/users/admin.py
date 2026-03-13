from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display  = ['username', 'nickname', 'email', 'streak_count', 'is_active', 'date_joined']
    list_filter   = ['is_active', 'is_staff']
    search_fields = ['username', 'nickname', 'email']
    fieldsets = UserAdmin.fieldsets + (
        ('타임밸런스 설정', {
            'fields': (
                'nickname',
                'streak_criteria', 'streak_count',
                'goal_daily_seconds', 'goal_weekly_seconds',
                'last_reset_week',
                'notif_goal', 'notif_remind', 'notif_balance_warn',
            )
        }),
    )
