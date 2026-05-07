from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_gift_card(request):
    return Response({'message': 'Gift card created'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_balance(request):
    return Response({'balance': 0})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def redeem_gift_card(request):
    return Response({'message': 'Gift card redeemed'})
