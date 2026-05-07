# apps/reviews/serializers.py
from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField(read_only=True)
    worker_name = serializers.SerializerMethodField(read_only=True)
    service_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'customer', 'customer_name', 'worker', 'worker_name',
            'service', 'service_name', 'rating', 'comment', 'photos',
            'is_approved', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'customer', 'created_at', 'updated_at', 
                           'customer_name', 'worker_name', 'service_name', 'photos']
        extra_kwargs = {
            'comment': {'required': True, 'allow_blank': False},
            'rating': {'required': True, 'min_value': 1, 'max_value': 5},
            'photos': {'required': False, 'default': list},
        }
    
    def get_customer_name(self, obj):
        if obj.customer:
            return obj.customer.get_full_name() or obj.customer.username
        return 'Anonymous'
    
    def get_worker_name(self, obj):
        if obj.worker:
            return obj.worker.get_full_name() or obj.worker.username
        return ''
    
    def get_service_name(self, obj):
        if obj.service:
            return obj.service.name
        return ''
    
    def validate_comment(self, value):
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Review must be at least 10 characters long")
        return value.strip()
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value