from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from apps.bookings.models import Booking
from apps.payments.models import Payment
from apps.accounts.models import User

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    if request.user.role != 'admin':
        return Response({'error': 'Admin access required'}, status=403)
    
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    total_bookings = Booking.objects.count()
    completed_bookings = Booking.objects.filter(status='completed').count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    
    total_revenue = Payment.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    total_customers = User.objects.filter(role='customer').count()
    
    weekly_bookings = Booking.objects.filter(created_at__date__gte=week_ago).count()
    weekly_revenue = Payment.objects.filter(created_at__date__gte=week_ago, status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    
    return Response({
        'total_bookings': total_bookings,
        'completed_bookings': completed_bookings,
        'pending_bookings': pending_bookings,
        'completion_rate': round((completed_bookings / total_bookings * 100) if total_bookings > 0 else 0, 1),
        'total_revenue': float(total_revenue),
        'total_customers': total_customers,
        'weekly_bookings': weekly_bookings,
        'weekly_revenue': float(weekly_revenue),
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_activities(request):
    if request.user.role != 'admin':
        return Response({'error': 'Admin access required'}, status=403)
    
    recent_bookings = Booking.objects.select_related('customer').order_by('-created_at')[:10]
    
    activities = []
    for booking in recent_bookings:
        activities.append({
            'id': str(booking.id),
            'type': 'booking',
            'customer': booking.customer.get_full_name(),
            'status': booking.status,
            'amount': float(booking.total_amount),
            'time': booking.created_at.isoformat(),
        })
    
    return Response(activities)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def calendar_overview(request):
    if request.user.role != 'admin':
        return Response({'error': 'Admin access required'}, status=403)
    
    bookings = Booking.objects.select_related('customer', 'worker').all()[:50]
    
    events = []
    for booking in bookings:
        events.append({
            'id': str(booking.id),
            'title': f"{booking.customer.get_full_name()} - Service",
            'start': booking.booking_date.isoformat(),
            'time': booking.time_slot.strftime('%H:%M') if booking.time_slot else '',
            'status': booking.status,
            'customer': booking.customer.get_full_name(),
        })
    
    return Response(events)
