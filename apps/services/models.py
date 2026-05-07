from django.db import models
from django.core.validators import MinValueValidator

class Service(models.Model):
    CATEGORY_CHOICES = [
        ('hair_styling', 'Hair Styling'),
        ('hair_color', 'Hair Color'),
        ('hair_treatment', 'Hair Treatment'),
        ('skincare', 'Skincare'),
        ('nails', 'Nails'),
        ('makeup', 'Makeup'),
        ('wellness', 'Wellness'),
        ('package', 'Package'),
    ]
    
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    mobile_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    after_hours_addon = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duration_minutes = models.IntegerField(validators=[MinValueValidator(15)])
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'services'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} - ${self.base_price}"
    
    @property
    def rating(self):
        from apps.reviews.models import Review
        reviews = Review.objects.filter(service=self, is_approved=True)
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 1)
        return 0

class ServiceImage(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='services/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'service_images'
        ordering = ['order']
    
    def __str__(self):
        return f"Image for {self.service.name}"
