# apps/settings/views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import SalonSettings
from .serializers import SalonSettingsSerializer


@api_view(['GET', 'PUT', 'POST'])
@permission_classes([IsAuthenticated])
def settings_handler(request):
    """
    Handle salon settings:
    - GET: Retrieve current settings
    - PUT: Update existing settings or create if not exists
    - POST: Create new settings
    """
    
    # Only admins can modify settings
    if request.method in ['PUT', 'POST'] and request.user.role != 'admin':
        return Response(
            {'error': 'Only administrators can modify settings'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get existing settings
    settings = SalonSettings.get_settings()
    
    if request.method == 'GET':
        serializer = SalonSettingsSerializer(settings)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = SalonSettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'POST':
        serializer = SalonSettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_public_settings(request):
    """Get public settings (non-sensitive info only) - No auth required"""
    try:
        settings = SalonSettings.get_settings()
        
        data = {
            'salon_name': settings.salon_name,
            'phone': settings.phone,
            'email': settings.email,
            'full_address': settings.full_address,
            'city': settings.city,
            'province': settings.province,
            'country': settings.country,
            'opening_time': settings.opening_time_formatted,
            'closing_time': settings.closing_time_formatted,
            'working_days': settings.working_days,
            'currency': settings.currency,
            'currency_symbol': settings.currency_symbol,
            'allow_online_booking': settings.allow_online_booking,
            'require_deposit': settings.require_deposit,
            'deposit_percentage': str(settings.deposit_percentage),
            'timezone': settings.timezone,
            'is_open_today': settings.is_open_today,
            'cancellation_policy': settings.cancellation_policy,
        }
        return Response(data)
    except Exception as e:
        return Response({
            'salon_name': 'SalonPro',
            'currency': 'ZMW',
            'currency_symbol': 'ZMW',
            'timezone': 'Africa/Lusaka',
            'country': 'Zambia',
            'error': str(e)
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initialize_default_settings(request):
    """Initialize settings with default values if they don't exist"""
    if request.user.role != 'admin':
        return Response(
            {'error': 'Only administrators can initialize settings'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    settings = SalonSettings.get_settings()
    serializer = SalonSettingsSerializer(settings)
    return Response({
        'message': 'Settings are ready',
        'settings': serializer.data
    })