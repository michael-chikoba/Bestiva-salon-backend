from rest_framework import serializers
from .models import AnalyticsEvent

class AnalyticsEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsEvent
        fields = ['id', 'user', 'event_type', 'data', 'ip_address', 'user_agent', 'created_at']
        read_only_fields = ['id', 'created_at']
