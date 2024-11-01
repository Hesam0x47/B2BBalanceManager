from rest_framework import serializers

from .models import BalanceIncreaseRequestModel, Sell
from ..accounts.models import SellerProfile


class BalanceIncreaseRequestSerializer(serializers.ModelSerializer):
    seller = serializers.SlugRelatedField(
        queryset=SellerProfile.objects.select_related("user"),
        slug_field='user__username',
    )

    class Meta:
        model = BalanceIncreaseRequestModel
        fields = ['id', 'seller', 'amount', 'status', 'timestamp']
        read_only_fields = ['status']


class ChargeCustomerSerializer(serializers.ModelSerializer):
    seller = serializers.SlugRelatedField(
        queryset=SellerProfile.objects.select_related("user"),
        slug_field='user__username',
    )

    class Meta:
        model = Sell
        fields = ['id', 'seller', 'phone_number', 'amount', 'timestamp']
        read_only_fields = ['timestamp']
