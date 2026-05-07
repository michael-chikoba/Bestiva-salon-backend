from django.db import models
from django.conf import settings


class Worker(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='worker_profile'
    )
    skills = models.JSONField(default=list)
    working_hours = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    hire_date = models.DateField(auto_now_add=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=12.0)

    class Meta:
        db_table = 'workers'

    def __str__(self):
        try:
            if self.user:
                return self.user.get_full_name() or self.user.username or f'Worker {self.id}'
        except Exception:
            pass
        return f'Worker {self.id}'


class Availability(models.Model):
    worker = models.ForeignKey(
        Worker,
        on_delete=models.CASCADE,
        related_name='availabilities'
    )
    date = models.DateField()
    is_leave = models.BooleanField(default=False)
    time_slots = models.JSONField(default=list)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'availabilities'
        unique_together = ['worker', 'date']

    def __str__(self):
        try:
            if self.worker and self.worker.user:
                name = self.worker.user.get_full_name() or self.worker.user.username or f'Worker {self.worker.id}'
                return f'{name} - {self.date}'
        except Exception:
            pass
        return f'Availability {self.id} - {self.date}'