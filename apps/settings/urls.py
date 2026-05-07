# apps/settings/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.settings_handler, name='settings'),
    path('public/', views.get_public_settings, name='public-settings'),
    path('initialize/', views.initialize_default_settings, name='initialize-settings'),
]