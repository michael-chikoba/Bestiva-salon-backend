from django.urls import path
from . import views

urlpatterns = [
    path('join/', views.join_waitlist, name='join-waitlist'),
    path('position/', views.check_position, name='check-position'),
    path('leave/', views.leave_waitlist, name='leave-waitlist'),
]
