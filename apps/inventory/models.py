# apps/inventory/models.py
from django.db import models
from django.core.validators import MinValueValidator

class InventoryItem(models.Model):
    CATEGORY_CHOICES = [
        ('hair', 'Hair Products'),
        ('nails', 'Nail Products'),
        ('skin', 'Skin Care'),
        ('tools', 'Tools & Equipment'),
        ('other', 'Other'),
    ]
    
    UNIT_CHOICES = [
        ('pieces', 'Pieces'),
        ('bottles', 'Bottles'),
        ('boxes', 'Boxes'),
        ('sets', 'Sets'),
        ('liters', 'Liters'),
        ('ml', 'Milliliters'),
        ('grams', 'Grams'),
        ('kg', 'Kilograms'),
    ]
    
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    sku = models.CharField(max_length=100, unique=True)
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    min_stock_level = models.IntegerField(default=10)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit_type = models.CharField(max_length=20, choices=UNIT_CHOICES, default='pieces')
    supplier = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'inventory_items'
        app_label = 'inventory'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.name} - {self.quantity} units"
    
    @property
    def status(self):
        if self.quantity <= 0:
            return 'Out of Stock'
        elif self.quantity <= self.min_stock_level:
            return 'Low Stock'
        elif self.quantity <= self.min_stock_level * 2:
            return 'Running Low'
        return 'In Stock'
    
    @property
    def stock_value(self):
        return float(self.quantity * self.unit_price)


class InventoryTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
        ('adjustment', 'Adjustment'),
        ('return', 'Return'),
    ]
    
    item = models.ForeignKey(
        InventoryItem, 
        on_delete=models.CASCADE, 
        related_name='transactions'
    )
    transaction_type = models.CharField(
        max_length=20, 
        choices=TRANSACTION_TYPES
    )
    quantity = models.IntegerField()
    previous_quantity = models.IntegerField()
    new_quantity = models.IntegerField()
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        'accounts.User', 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'inventory_transactions'
        app_label = 'inventory'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.item.name}: {self.quantity}"