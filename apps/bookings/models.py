from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
import uuid


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]

    TYPE_CHOICES = [
        ('in_salon', 'In Salon'),
        ('mobile', 'Mobile Service'),
    ]

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    worker       = models.ForeignKey('employees.Worker', on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    booking_date = models.DateField()
    time_slot    = models.TimeField()
    type         = models.CharField(max_length=20, choices=TYPE_CHOICES, default='in_salon')
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes        = models.TextField(blank=True, null=True)
    qr_code      = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bookings'
        ordering = ['-booking_date', '-time_slot']

    def __str__(self):
        try:
            return f"Booking {self.id} - {self.customer.get_full_name() or self.customer.username}"
        except Exception:
            return f"Booking {self.id}"

    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def deposit_amount(self):
        # Use Decimal to avoid TypeError when multiplying Decimal * float
        return self.total_amount * Decimal('0.3')


class BookingItem(models.Model):
    booking        = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='items')
    service        = models.ForeignKey('services.Service', on_delete=models.CASCADE)
    quantity       = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    price_at_time  = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'booking_items'

    @property
    def total_price(self):
        return self.price_at_time * self.quantity

    def __str__(self):
        try:
            return f"{self.booking.id} - {self.service.name}"
        except Exception:
            return f"BookingItem {self.id}"


class WorkCompletion(models.Model):
    booking      = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='completion')
    worker       = models.ForeignKey('employees.Worker', on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)
    photos       = models.JSONField(default=list)
    notes        = models.TextField(blank=True, null=True)
    products_used = models.JSONField(default=list)

    class Meta:
        db_table = 'work_completions'

    def __str__(self):
        try:
            return f"Completion for {self.booking.id}"
        except Exception:
            return f"WorkCompletion {self.id}"