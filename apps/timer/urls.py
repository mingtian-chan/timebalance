from django.urls import path
from . import views

urlpatterns = [
    path('records/',              views.save_record,   name='save-record'),
    path('records/list/',         views.list_records,  name='list-records'),
    path('records/<int:record_id>/delete/', views.delete_record, name='delete-record'),
    path('weekly-status/',        views.weekly_status, name='weekly-status'),
    path('reset-history/',        views.reset_history, name='reset-history'),
]
