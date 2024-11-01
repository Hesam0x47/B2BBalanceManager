from rest_framework import serializers

from apps.accounts.models import SellerProfile


class SellerApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerProfile
        fields = ['is_verified']
        read_only_fields = ['is_verified']

    def update(self, instance, validated_data):
        instance.is_verified = True
        instance.save()
        return instance
