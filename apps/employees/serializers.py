from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Worker, Availability

User = get_user_model()


class UserSimpleSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'phone', 'role', 'name']

    def get_name(self, obj):
        if obj is None:
            return ''
        return obj.get_full_name() or obj.username or ''


class WorkerSerializer(serializers.ModelSerializer):
    user_details = UserSimpleSerializer(source='user', read_only=True)
    name     = serializers.SerializerMethodField()
    email    = serializers.SerializerMethodField()
    phone    = serializers.SerializerMethodField()
    position = serializers.SerializerMethodField()

    class Meta:
        model = Worker
        fields = [
            'id', 'user', 'user_details', 'name', 'email', 'phone',
            'position', 'skills', 'working_hours', 'is_active',
            'hire_date', 'commission_rate',
        ]
        read_only_fields = ['id', 'hire_date']

    def _safe_user(self, obj):
        """Return user or None without raising."""
        try:
            return obj.user
        except Exception:
            return None

    def get_name(self, obj):
        user = self._safe_user(obj)
        if not user:
            return 'Unknown'
        return user.get_full_name() or user.username or 'Unknown'

    def get_email(self, obj):
        user = self._safe_user(obj)
        return (user.email or '') if user else ''

    def get_phone(self, obj):
        user = self._safe_user(obj)
        if not user:
            return ''
        return getattr(user, 'phone', '') or ''

    def get_position(self, obj):
        user = self._safe_user(obj)
        if not user:
            return 'Staff'
        # 'position' is an optional field on the custom User model
        return getattr(user, 'position', None) or 'Staff'


class AvailabilitySerializer(serializers.ModelSerializer):
    worker_name = serializers.SerializerMethodField()

    class Meta:
        model = Availability
        fields = ['id', 'worker', 'worker_name', 'date',
                  'is_leave', 'time_slots', 'notes']

    def get_worker_name(self, obj):
        try:
            if obj.worker and obj.worker.user:
                return obj.worker.user.get_full_name() or 'Unknown'
        except Exception:
            pass
        return 'Unknown'