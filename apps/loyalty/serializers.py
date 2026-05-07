from rest_framework import serializers
from .models import LoyaltyTransaction, Reward, RewardRedemption

class LoyaltyTransactionSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    
    class Meta:
        model = LoyaltyTransaction
        fields = ['id', 'customer', 'customer_name', 'points', 'transaction_type', 
                  'description', 'related_booking', 'created_at', 'expires_at']
        read_only_fields = ['id', 'created_at']

class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

class RewardRedemptionSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    reward_name = serializers.CharField(source='reward.name', read_only=True)
    
    class Meta:
        model = RewardRedemption
        fields = ['id', 'customer', 'customer_name', 'reward', 'reward_name', 
                  'points_used', 'redeemed_at']
        read_only_fields = ['id', 'redeemed_at']
