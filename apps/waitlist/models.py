from django.db import models
from django.conf import settings

class WaitlistEntry(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE)
    preferred_date = models.DateField()
    preferred_time = models.TimeField(null=True, blank=True)
    position = models.IntegerField()
    status = models.CharField(max_length=20, default='waiting')
    notified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'waitlist'
        app_label = 'waitlist'
    
    def __str__(self):
        return f"{self.customer.get_full_name()} - Position {self.position}"
