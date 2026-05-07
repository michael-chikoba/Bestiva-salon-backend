from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_promo_code(request):
    return Response({'message': 'Promo code created'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_promo_code(request):
    return Response({'valid': True})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_promo_code(request):
    return Response({'message': 'Promo code applied'})
