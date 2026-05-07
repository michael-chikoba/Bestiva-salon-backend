from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('employee', 'Employee'),
        ('customer', 'Customer'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Customer specific fields
    loyalty_points = models.IntegerField(default=0)
    loyalty_tier = models.CharField(max_length=20, default='Bronze')

    # Employee specific fields
    employee_id = models.CharField(max_length=50, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']

    def __str__(self):
        try:
            name = self.get_full_name() or self.username or 'Unknown'
            return f"{name} ({self.role})"
        except Exception:
            return f"User {self.pk}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        # First save — lets the DB assign self.id / self.pk
        super().save(*args, **kwargs)

        # After first save we have a real PK, so we can build employee_id
        if is_new and self.role == 'employee' and not self.employee_id:
            self.employee_id = f"EMP{self.pk:05d}"
            # Only update the one field — avoids recursion and is efficient
            super().save(update_fields=['employee_id'])


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    preferences = models.JSONField(default=dict)

    class Meta:
        db_table = 'user_profiles'

    def __str__(self):
        try:
            return f"{self.user.get_full_name() or self.user.username}'s Profile"
        except Exception:
            return f"Profile {self.pk}"


class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        db_table = 'password_resets'

    def __str__(self):
        try:
            return f"Reset token for {self.user.email}"
        except Exception:
            return f"PasswordReset {self.pk}"