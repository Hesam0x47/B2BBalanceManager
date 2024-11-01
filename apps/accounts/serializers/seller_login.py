from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class SellerLoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Ensure the user has a seller profile and is verified
        if not hasattr(self.user, 'seller_profile') or not self.user.seller_profile.is_verified:
            raise serializers.ValidationError("Your account is not verified. Please contact support.")

        return data
