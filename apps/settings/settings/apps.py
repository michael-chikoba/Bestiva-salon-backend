# apps/settings/apps.py
from django.apps import AppConfig


class SettingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.settings'
    verbose_name = 'Salon Settings'
    
    def ready(self):
        """Initialize default settings when app is ready"""
        try:
            from .models import SalonSettings
            # Ensure default settings exist
            SalonSettings.get_settings()
        except Exception:
            # Handle cases where tables don't exist yet (during migrations)
            pass