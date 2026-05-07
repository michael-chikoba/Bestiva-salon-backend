# apps/inventory/serializers.py
from rest_framework import serializers
from .models import InventoryItem, InventoryTransaction


class InventoryItemSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    stock_value = serializers.SerializerMethodField()
    
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'name', 'category', 'description', 'sku',
            'quantity', 'min_stock_level', 'unit_price',
            'supplier', 'location', 'is_active',
            'created_at', 'updated_at', 'status', 'stock_value'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'status', 'stock_value']
    
    def get_status(self, obj):
        """Determine stock status"""
        if obj.quantity <= 0:
            return 'Out of Stock'
        elif obj.quantity <= obj.min_stock_level:
            return 'Low Stock'
        elif obj.quantity <= obj.min_stock_level * 2:
            return 'Running Low'
        return 'In Stock'
    
    def get_stock_value(self, obj):
        """Calculate total stock value"""
        return float(obj.quantity * obj.unit_price)
    
    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative")
        return value
    
    def validate_unit_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative")
        return value
    
    def validate_min_stock_level(self, value):
        if value < 0:
            raise serializers.ValidationError("Minimum stock level cannot be negative")
        return value


class InventoryTransactionSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = InventoryTransaction
        fields = [
            'id', 'item', 'item_name', 'transaction_type',
            'quantity', 'previous_quantity', 'new_quantity',
            'notes', 'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'created_by']
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return 'System'