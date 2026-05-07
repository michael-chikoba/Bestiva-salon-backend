from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import LoyaltyTransaction, Reward, RewardRedemption
from .serializers import LoyaltyTransactionSerializer, RewardSerializer, RewardRedemptionSerializer

class LoyaltyTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LoyaltyTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return LoyaltyTransaction.objects.all()
        return LoyaltyTransaction.objects.filter(customer=user)

class RewardViewSet(viewsets.ModelViewSet):
    serializer_class = RewardSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Reward.objects.all()
        return Reward.objects.filter(is_active=True)
    
    @action(detail=True, methods=['post'])
    def redeem(self, request, pk=None):
        reward = self.get_object()
        user = request.user
        
        if user.loyalty_points < reward.points_required:
            return Response({'error': 'Insufficient points'}, status=status.HTTP_400_BAD_REQUEST)
        
        transaction = LoyaltyTransaction.objects.create(
            customer=user,
            points=-reward.points_required,
            transaction_type='redeemed',
            description=f"Redeemed: {reward.name}"
        )
        
        RewardRedemption.objects.create(
            customer=user,
            reward=reward,
            points_used=reward.points_required,
            transaction=transaction
        )
        
        user.loyalty_points -= reward.points_required
        user.save()
        
        return Response({
            'message': f'Successfully redeemed {reward.name}',
            'points_remaining': user.loyalty_points
        })
