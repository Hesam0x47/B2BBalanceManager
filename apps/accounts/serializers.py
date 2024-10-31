from django.db import transaction
from rest_framework import serializers

from .models import User, SellerProfile, CustomerProfile, AdminProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class SellerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = SellerProfile
        fields = ['user', 'balance', 'company_name', 'is_verified']

    @transaction.atomic
    def create(self, validated_data):
        # Extract the nested user data
        user_data = validated_data.pop('user')

        # Create the User instance
        user = User.objects.create(**user_data)

        # Create the SellerProfile instance and associate it with the User
        seller_profile = SellerProfile.objects.create(user=user, **validated_data)

        return seller_profile


# class CustomerProfileSerializer(serializers.ModelSerializer):
#     user = UserSerializer()
#
#     class Meta:
#         model = CustomerProfile
#         fields = ['user', 'address', 'loyalty_points']
#
#
# class AdminProfileSerializer(serializers.ModelSerializer):
#     user = UserSerializer()
#
#     class Meta:
#         model = AdminProfile
#         fields = ['user', 'department']
