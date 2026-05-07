from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import WaitlistEntry
from apps.services.models import Service

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_waitlist(request):
    service_id = request.data.get('service_id')
    
    try:
        service = Service.objects.get(id=service_id, is_active=True)
    except Service.DoesNotExist:
        return Response({'error': 'Service not found'}, status=404)
    
    current_count = WaitlistEntry.objects.filter(service=service, status='waiting').count()
    
    entry = WaitlistEntry.objects.create(
        customer=request.user,
        service=service,
        preferred_date=request.data.get('preferred_date'),
        position=current_count + 1
    )
    
    return Response({'message': 'Added to waitlist', 'position': entry.position})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_position(request):
    service_id = request.query_params.get('service_id')
    
    try:
        entry = WaitlistEntry.objects.get(customer=request.user, service_id=service_id, status='waiting')
        return Response({'position': entry.position})
    except WaitlistEntry.DoesNotExist:
        return Response({'message': 'Not on waitlist'}, status=404)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def leave_waitlist(request):
    service_id = request.data.get('service_id')
    
    try:
        entry = WaitlistEntry.objects.get(customer=request.user, service_id=service_id, status='waiting')
        entry.delete()
        return Response({'message': 'Removed from waitlist'})
    except WaitlistEntry.DoesNotExist:
        return Response({'error': 'Not on waitlist'}, status=404)
