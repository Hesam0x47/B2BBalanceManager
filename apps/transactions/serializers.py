from rest_framework import serializers

from .models import BalanceIncreaseRequestModel, ChargeCustomerModel
from ..accounts.models import SellerProfile


class BalanceIncreaseRequestSerializer(serializers.ModelSerializer):
    seller = serializers.SlugRelatedField(
        queryset=SellerProfile.objects.select_related("user"),
        slug_field='user__username',
    )

    class Meta:
        model = BalanceIncreaseRequestModel
        fields = ['id', 'seller', 'amount', 'status', 'timestamp']
        read_only_fields = [
            'status',
            'seller',  # we get seller from request token authentication info
        ]

    def validate(self, attrs):
        requester_user = self.context['request'].user
        attrs["seller"] = requester_user.seller_profile  # TODO: refactor -> rename it to "seller_profile"
        return super().validate(attrs)


class ChargeCustomerSerializer(serializers.ModelSerializer):
    seller = serializers.SlugRelatedField(
        queryset=SellerProfile.objects.select_related("user"),
        slug_field='user__username',
    )

    class Meta:
        model = ChargeCustomerModel
        fields = [
            # 'id', # we do not show id in response because there is no saved instance and therefore id is always None
            'seller',
            'phone_number',
            'amount',
            'timestamp',
        ]
        read_only_fields = [
            'timestamp',
            'seller',  # we get seller from request token authentication info
        ]

    def validate(self, attrs):
        requester_user = self.context['request'].user
        attrs["seller"] = requester_user.seller_profile  # TODO: refactor -> rename it to "seller_profile"
        return super().validate(attrs)