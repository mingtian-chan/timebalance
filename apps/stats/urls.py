from django.urls import path
from . import views

urlpatterns = [
    path('daily/',   views.daily_summary,  name='daily-summary'),
    path('weekly/',  views.weekly_summary, name='weekly-summary'),
    path('today/',   views.today_summary,  name='today-summary'),
]
