# apps/settings/models.py
from django.db import models

class SalonSettings(models.Model):
    """Salon configuration settings - Singleton pattern"""
    
    # General Settings
    salon_name = models.CharField(
        max_length=200, 
        default='SalonPro',
        help_text='Name of your salon'
    )
    email = models.EmailField(
        default='info@salonpro.co.zm',
        help_text='Business email address'
    )
    phone = models.CharField(
        max_length=20, 
        default='+260',
        help_text='Business phone number'
    )
    address = models.TextField(
        blank=True, 
        null=True,
        help_text='Physical address'
    )
    city = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text='City'
    )
    province = models.CharField(
        max_length=100, 
        default='Lusaka',
        help_text='Province'
    )
    country = models.CharField(
        max_length=100, 
        default='Zambia',
        help_text='Country'
    )
    
    # Business Settings
    timezone = models.CharField(
        max_length=50, 
        default='Africa/Lusaka',
        help_text='Timezone for the business'
    )
    date_format = models.CharField(
        max_length=20, 
        default='DD/MM/YYYY',
        help_text='Date display format'
    )
    time_format = models.CharField(
        max_length=10, 
        default='12h',
        help_text='Time display format (12h or 24h)'
    )
    currency = models.CharField(
        max_length=10, 
        default='ZMW',
        help_text='Currency code (ZMW, USD, etc.)'
    )
    currency_symbol = models.CharField(
        max_length=10, 
        default='ZMW',
        help_text='Currency symbol'
    )
    tax_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=16.00,
        help_text='VAT/Tax rate percentage'
    )
    opening_time = models.TimeField(
        default='08:00',
        help_text='Business opening time'
    )
    closing_time = models.TimeField(
        default='18:00',
        help_text='Business closing time'
    )
    
    # Working Days (stored as JSON)
    working_days = models.JSONField(
        default=list,
        help_text='List of working days'
    )
    
    # Booking Settings
    booking_buffer = models.IntegerField(
        default=15,
        help_text='Buffer time between bookings in minutes'
    )
    max_bookings_per_slot = models.IntegerField(
        default=3,
        help_text='Maximum bookings per time slot'
    )
    cancellation_policy = models.TextField(
        default='24 hours notice required for cancellation',
        help_text='Cancellation policy text'
    )
    allow_online_booking = models.BooleanField(
        default=True,
        help_text='Enable online booking'
    )
    require_deposit = models.BooleanField(
        default=True,
        help_text='Require deposit for bookings'
    )
    deposit_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=30.00,
        help_text='Deposit percentage required'
    )
    
    # Notification Settings
    email_notifications = models.BooleanField(
        default=True,
        help_text='Enable email notifications'
    )
    sms_reminders = models.BooleanField(
        default=True,
        help_text='Enable SMS reminders'
    )
    booking_confirmations = models.BooleanField(
        default=True,
        help_text='Send booking confirmation emails'
    )
    marketing_emails = models.BooleanField(
        default=False,
        help_text='Send marketing/promotional emails'
    )
    review_notifications = models.BooleanField(
        default=True,
        help_text='Notify on new reviews'
    )
    inventory_alerts = models.BooleanField(
        default=True,
        help_text='Notify on low inventory'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'settings'
        db_table = 'salon_settings'
        verbose_name = 'Salon Settings'
        verbose_name_plural = 'Salon Settings'
    
    def __str__(self):
        return self.salon_name or 'Salon Settings'
    
    def save(self, *args, **kwargs):
        """Ensure only one settings instance exists (Singleton pattern)"""
        if not self.pk and SalonSettings.objects.exists():
            # If creating new and one already exists, update existing
            existing = SalonSettings.objects.first()
            self.pk = existing.pk
            # Copy all fields to existing instance
            for field in self._meta.fields:
                if field.name not in ['id', 'pk', 'created_at']:
                    setattr(existing, field.name, getattr(self, field.name, getattr(existing, field.name)))
            existing.save(*args, **kwargs)
            return
        
        # Set default working days if empty
        if not self.working_days:
            self.working_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        
        super().save(*args, **kwargs)
    
    @property
    def opening_time_formatted(self):
        """Return opening time as HH:MM string"""
        return self.opening_time.strftime('%H:%M') if self.opening_time else '08:00'
    
    @property
    def closing_time_formatted(self):
        """Return closing time as HH:MM string"""
        return self.closing_time.strftime('%H:%M') if self.closing_time else '18:00'
    
    @property
    def full_address(self):
        """Return formatted full address"""
        parts = []
        if self.address:
            parts.append(self.address)
        if self.city:
            parts.append(self.city)
        if self.province:
            parts.append(self.province)
        if self.country:
            parts.append(self.country)
        return ', '.join(parts) if parts else 'Address not set'
    
    @property
    def is_open_today(self):
        """Check if business is open today based on working days"""
        from datetime import datetime
        today = datetime.now().strftime('%A')
        return today in (self.working_days or [])
    
    @classmethod
    def get_settings(cls):
        """Get or create settings instance"""
        settings, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'salon_name': 'SalonPro',
                'working_days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
            }
        )
        return settings