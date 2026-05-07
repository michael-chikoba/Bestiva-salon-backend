import uuid
from django.db import models
from django.conf import settings

class GiftCard(models.Model):
    code = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    recipient_name = models.CharField(max_length=200)
    recipient_email = models.EmailField()
    message = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    redeemed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'gift_cards'
        app_label = 'giftcards'
    
    def __str__(self):
        return f"Gift Card {self.code} - ${self.balance}"

class GiftCardTransaction(models.Model):
    gift_card = models.ForeignKey(GiftCard, on_delete=models.CASCADE, related_name='transactions')
    booking = models.ForeignKey('bookings.Booking', on_delete=models.CASCADE)
    amount_used = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'gift_card_transactions'
        app_label = 'giftcards'
    
    def __str__(self):
        return f"Used ${self.amount_used} from {self.gift_card.code}"
