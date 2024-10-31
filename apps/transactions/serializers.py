from rest_framework import serializers

from .models import Recharge, Sell
from ..accounts.models import SellerProfile


class RechargeSerializer(serializers.ModelSerializer):
    seller = serializers.SlugRelatedField(queryset=SellerProfile.objects.select_related("user"),
                                          slug_field='user__username')

    class Meta:
        model = Recharge
        fields = ['id', 'seller', 'amount', 'status', 'timestamp']
        read_only_fields = ['status', 'created_at']


class SellSerializer(serializers.ModelSerializer):
    seller = serializers.SlugRelatedField(queryset=SellerProfile.objects.select_related("user"),
                                          slug_field='user__username')

    class Meta:
        model = Sell
        fields = ['id', 'seller', 'customer', 'amount', 'timestamp']
        read_only_fields = ['timestamp']
