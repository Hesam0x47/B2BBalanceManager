from rest_framework import serializers

from .models import BalanceIncreaseRequestModel, ChargeCustomerModel


class BalanceIncreaseRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BalanceIncreaseRequestModel
        fields = ['id', 'amount', 'status', 'timestamp']
        read_only_fields = [
            'status',
        ]

    def validate(self, attrs):
        requester_user = self.context['request'].user
        attrs["seller"] = requester_user.seller_profile  # TODO: refactor -> rename it to "seller_profile"
        return super().validate(attrs)


class ChargeCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChargeCustomerModel
        fields = [
            # 'id', # we do not show id in response because there is no saved instance and therefore id is always None
            'phone_number',
            'amount',
            'timestamp',
        ]
        read_only_fields = [
            'timestamp',
        ]

    def validate(self, attrs):
        requester_user = self.context['request'].user
        attrs["seller"] = requester_user.seller_profile  # TODO: refactor -> rename it to "seller_profile"
        return super().validate(attrs)