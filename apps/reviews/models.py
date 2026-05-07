# apps/reviews/models.py
from django.db import models
from django.conf import settings

class Review(models.Model):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='reviews'
    )
    worker = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='worker_reviews'
    )
    service = models.ForeignKey(
        'services.Service', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reviews'
    )
    rating = models.IntegerField(default=5)
    comment = models.TextField()
    photos = models.JSONField(default=list, blank=True)  # ✅ Add default=list and blank=True
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']
    
    def __str__(self):
        customer_name = self.customer.get_full_name() or self.customer.username if self.customer else 'Anonymous'
        return f"Review by {customer_name} - {self.rating}★"