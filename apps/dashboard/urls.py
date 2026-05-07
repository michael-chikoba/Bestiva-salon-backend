from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.dashboard_stats, name='dashboard-stats'),
    path('activities/', views.recent_activities, name='recent-activities'),
    path('calendar/', views.calendar_overview, name='calendar-overview'),
]
