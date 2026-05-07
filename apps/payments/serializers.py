from rest_framework import serializers
from .models import Payment, Refund

class PaymentSerializer(serializers.ModelSerializer):
    booking_id = serializers.CharField(source='booking.id', read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'booking', 'booking_id', 'amount', 'deposit_amount', 'method', 
                  'status', 'stripe_payment_intent_id', 'transaction_id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class RefundSerializer(serializers.ModelSerializer):
    booking_id = serializers.CharField(source='payment.booking.id', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = Refund
        fields = ['id', 'payment', 'booking_id', 'amount', 'reason', 'status', 
                  'approved_by', 'approved_by_name', 'net_refund', 'transaction_fee', 
                  'processed_at', 'notes']
        read_only_fields = ['id', 'processed_at', 'net_refund', 'transaction_fee']
