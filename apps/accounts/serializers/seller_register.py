from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from apps.accounts.models import SellerProfile

User = get_user_model()


class SellerRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    company_name = serializers.CharField(max_length=255, required=True, write_only=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({"username": "Username already registered."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        company_name = validated_data.pop('company_name', None)

        role = User.SELLER
        validated_data['role'] = role

        user = User.objects.create_user(**validated_data)
        SellerProfile.objects.create(user=user, company_name=company_name)
        return user
