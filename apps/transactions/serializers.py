from rest_framework import serializers

from .models import CreditIncreaseRequestModel, Sell
from ..accounts.models import SellerProfile


class CreditIncreaseRequestSerializer(serializers.ModelSerializer):
    seller = serializers.SlugRelatedField(
        queryset=SellerProfile.objects.select_related("user"),
        slug_field='user__username',
    )

    class Meta:
        model = CreditIncreaseRequestModel
        fields = ['id', 'seller', 'amount', 'status', 'timestamp']
        read_only_fields = ['status']


class SellSerializer(serializers.ModelSerializer):
    seller = serializers.SlugRelatedField(queryset=SellerProfile.objects.select_related("user"),
                                          slug_field='user__username')

    class Meta:
        model = Sell
        fields = ['id', 'seller', 'customer', 'amount', 'timestamp']
        read_only_fields = ['timestamp']
