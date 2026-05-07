# apps/services/serializers.py
from rest_framework import serializers
from .models import Service, ServiceImage

class ServiceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceImage
        fields = ['id', 'image', 'caption', 'order']

class ServiceSerializer(serializers.ModelSerializer):
    images = ServiceImageSerializer(many=True, read_only=True)
    rating = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Service
        fields = [
            'id', 'name', 'category', 'description', 'base_price', 
            'mobile_price', 'after_hours_addon', 'duration_minutes', 
            'is_active', 'image', 'images', 'rating', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'rating']
    
    def validate_base_price(self, value):
        """Validate base price"""
        if value is None or value < 0:
            raise serializers.ValidationError("Base price must be a positive number")
        return value
    
    def validate_duration_minutes(self, value):
        """Validate duration"""
        if value is None or value < 15:
            raise serializers.ValidationError("Duration must be at least 15 minutes")
        return value
    
    def validate_name(self, value):
        """Validate name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Service name is required")
        return value.strip()
    
    def validate(self, data):
        """Cross-field validation"""
        # Ensure mobile_price is set or null
        if 'mobile_price' in data and data['mobile_price'] == '':
            data['mobile_price'] = None
        
        # Ensure after_hours_addon has a default
        if 'after_hours_addon' not in data or data.get('after_hours_addon') is None:
            data['after_hours_addon'] = 0
        
        return data