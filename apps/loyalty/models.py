from django.db import models
from django.conf import settings

class LoyaltyTransaction(models.Model):
    TYPE_CHOICES = [
        ('earned', 'Points Earned'),
        ('redeemed', 'Points Redeemed'),
        ('bonus', 'Bonus Points'),
        ('expired', 'Points Expired'),
    ]
    
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loyalty_transactions')
    points = models.IntegerField()
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.CharField(max_length=255)
    related_booking = models.ForeignKey('bookings.Booking', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'loyalty_transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer.get_full_name()} - {self.transaction_type}: {self.points}"

class Reward(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    points_required = models.IntegerField()
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_percentage = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'rewards'
    
    def __str__(self):
        return f"{self.name} - {self.points_required} points"

class RewardRedemption(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='redemptions')
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    points_used = models.IntegerField()
    transaction = models.ForeignKey(LoyaltyTransaction, on_delete=models.CASCADE, related_name='redemption')
    redeemed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'reward_redemptions'
    
    def __str__(self):
        return f"{self.customer.get_full_name()} redeemed {self.reward.name}"
