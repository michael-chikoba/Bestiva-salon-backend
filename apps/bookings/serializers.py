from rest_framework import serializers
from .models import Booking, BookingItem, WorkCompletion
from apps.services.serializers import ServiceSerializer

class BookingItemSerializer(serializers.ModelSerializer):
    service_details = ServiceSerializer(source='service', read_only=True)
    
    class Meta:
        model = BookingItem
        fields = ['id', 'service', 'service_details', 'quantity', 'price_at_time', 'total_price']
        read_only_fields = ['total_price']

class BookingSerializer(serializers.ModelSerializer):
    items = BookingItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    deposit_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Booking
        fields = ['id', 'customer', 'customer_name', 'worker', 'booking_date', 'time_slot', 
                  'type', 'status', 'notes', 'qr_code', 'items', 'total_amount', 
                  'deposit_amount', 'created_at', 'updated_at']
        read_only_fields = ['id', 'qr_code', 'created_at', 'updated_at', 'total_amount', 'deposit_amount']

class WorkCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkCompletion
        fields = ['id', 'booking', 'worker', 'completed_at', 'photos', 'notes', 'products_used']
        read_only_fields = ['id', 'completed_at']

class CreateBookingSerializer(serializers.Serializer):
    booking_date = serializers.DateField()
    time_slot = serializers.TimeField()
    type = serializers.ChoiceField(choices=['in_salon', 'mobile'])
    service_items = serializers.ListField(child=serializers.DictField())
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_service_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one service is required")
        return value
