# apps/settings/serializers.py
from rest_framework import serializers
from .models import SalonSettings

class SalonSettingsSerializer(serializers.ModelSerializer):
    # Time fields with proper format handling
    opening_time = serializers.TimeField(
        format='%H:%M', 
        input_formats=['%H:%M', '%H:%M:%S'],
        required=False,
        default='08:00'
    )
    closing_time = serializers.TimeField(
        format='%H:%M', 
        input_formats=['%H:%M', '%H:%M:%S'],
        required=False,
        default='18:00'
    )
    
    class Meta:
        model = SalonSettings
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_working_days(self, value):
        """Validate working days"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Working days must be a list")
        
        valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day in value:
            if day not in valid_days:
                raise serializers.ValidationError(f"'{day}' is not a valid day")
        
        if len(value) == 0:
            raise serializers.ValidationError("At least one working day is required")
        
        return value
    
    def validate_tax_rate(self, value):
        """Validate tax rate"""
        try:
            tax_rate = float(value)
        except (TypeError, ValueError):
            raise serializers.ValidationError("Tax rate must be a number")
        
        if tax_rate < 0 or tax_rate > 100:
            raise serializers.ValidationError("Tax rate must be between 0 and 100")
        
        return value
    
    def validate_deposit_percentage(self, value):
        """Validate deposit percentage"""
        try:
            deposit = float(value)
        except (TypeError, ValueError):
            raise serializers.ValidationError("Deposit percentage must be a number")
        
        if deposit < 0 or deposit > 100:
            raise serializers.ValidationError("Deposit percentage must be between 0 and 100")
        
        return value
    
    def validate_booking_buffer(self, value):
        """Validate booking buffer"""
        try:
            buffer = int(value)
        except (TypeError, ValueError):
            raise serializers.ValidationError("Booking buffer must be a number")
        
        if buffer < 0 or buffer > 120:
            raise serializers.ValidationError("Booking buffer must be between 0 and 120 minutes")
        
        return value
    
    def validate_max_bookings_per_slot(self, value):
        """Validate max bookings per slot"""
        try:
            max_bookings = int(value)
        except (TypeError, ValueError):
            raise serializers.ValidationError("Max bookings per slot must be a number")
        
        if max_bookings < 1 or max_bookings > 50:
            raise serializers.ValidationError("Max bookings per slot must be between 1 and 50")
        
        return value
    
    def validate_email(self, value):
        """Validate email format"""
        if value and '@' not in value:
            raise serializers.ValidationError("Please enter a valid email address")
        return value
    
    def validate_phone(self, value):
        """Validate phone number"""
        if value and len(value) < 10:
            raise serializers.ValidationError("Phone number seems too short")
        return value
    
    def validate_salon_name(self, value):
        """Validate salon name"""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Salon name must be at least 2 characters")
        return value.strip()
    
    def validate_currency(self, value):
        """Validate currency"""
        valid_currencies = ['ZMW', 'USD', 'ZAR', 'EUR', 'GBP']
        if value and value not in valid_currencies:
            raise serializers.ValidationError(f"Currency must be one of: {', '.join(valid_currencies)}")
        return value
    
    def validate_timezone(self, value):
        """Validate timezone"""
        valid_timezones = [
            'Africa/Lusaka', 'Africa/Johannesburg', 'Africa/Harare',
            'Africa/Nairobi', 'Africa/Lagos', 'Africa/Cairo',
            'America/New_York', 'America/Chicago', 'America/Los_Angeles',
            'Europe/London', 'Europe/Paris', 'Asia/Tokyo', 'Asia/Dubai'
        ]
        if value and value not in valid_timezones:
            raise serializers.ValidationError(f"Invalid timezone: {value}")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        # Validate opening time is before closing time
        opening_time = data.get('opening_time')
        closing_time = data.get('closing_time')
        
        if opening_time and closing_time:
            if opening_time >= closing_time:
                raise serializers.ValidationError({
                    'closing_time': 'Closing time must be after opening time'
                })
        
        # Validate deposit percentage is required when deposits are enabled
        require_deposit = data.get('require_deposit', True)
        deposit_percentage = data.get('deposit_percentage', 0)
        
        if require_deposit and (not deposit_percentage or float(deposit_percentage) <= 0):
            raise serializers.ValidationError({
                'deposit_percentage': 'Deposit percentage is required when deposits are enabled'
            })
        
        return data
    
    def to_representation(self, instance):
        """Customize output representation"""
        data = super().to_representation(instance)
        
        # Ensure time fields are formatted correctly
        if 'opening_time' in data and data['opening_time']:
            data['opening_time'] = data['opening_time'][:5]  # Return HH:MM format
        
        if 'closing_time' in data and data['closing_time']:
            data['closing_time'] = data['closing_time'][:5]  # Return HH:MM format
        
        # Ensure numeric fields are returned as strings for consistency
        for field in ['tax_rate', 'deposit_percentage']:
            if field in data and data[field] is not None:
                data[field] = str(data[field])
        
        return data
    
    def to_internal_value(self, data):
        """Customize input parsing"""
        # Handle time fields that might come as strings
        if 'opening_time' in data and isinstance(data['opening_time'], str):
            if len(data['opening_time']) > 5:
                data['opening_time'] = data['opening_time'][:5]
            if not data['opening_time']:
                data['opening_time'] = '08:00'
        
        if 'closing_time' in data and isinstance(data['closing_time'], str):
            if len(data['closing_time']) > 5:
                data['closing_time'] = data['closing_time'][:5]
            if not data['closing_time']:
                data['closing_time'] = '18:00'
        
        # Convert empty strings to appropriate types
        for field in ['address', 'city', 'province']:
            if field in data and data[field] == '':
                data[field] = None
        
        # Convert numeric strings
        for field in ['tax_rate', 'deposit_percentage', 'booking_buffer', 'max_bookings_per_slot']:
            if field in data and isinstance(data[field], str) and data[field].strip() == '':
                data.pop(field, None)  # Remove empty values to use defaults
        
        return super().to_internal_value(data)