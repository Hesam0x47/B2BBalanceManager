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
        fields = ['id', 'seller', 'telephone', 'amount', 'timestamp']
        read_only_fields = ['timestamp']


# class ChargeCustomerSerializer(serializers.Serializer):
#     seller = serializers.SlugRelatedField(queryset=SellerProfile.objects.select_related("user"),
#                                           slug_field='user__username')
#     customer_id = serializers.IntegerField(required=True)
#     amount = serializers.DecimalField(max_digits=6, decimal_places=2, min_value=5000, max_value=100000)
#
#     def validate_amount(self, value):
#         if value <= 0:
#             raise serializers.ValidationError("Amount must be greater than zero.")
#         return value
