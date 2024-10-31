from rest_framework import serializers
from .models import Recharge, Seller


class RechargeSerializer(serializers.ModelSerializer):
    seller = serializers.SlugRelatedField(queryset=Seller.objects.all(), slug_field='email')

    class Meta:
        model = Recharge
        fields = ['id', 'seller', 'amount', 'is_successful', 'status', 'created_at']
        read_only_fields = ['is_successful', 'status', 'created_at']

    def create(self, validated_data):
        recharge = Recharge.objects.create(**validated_data)
        return recharge
