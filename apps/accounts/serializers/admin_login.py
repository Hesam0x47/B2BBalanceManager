from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class AdminTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        self.__check_if_user_is_admin()
        return data

    def __check_if_user_is_admin(self):
        if not self.user.is_staff:
            raise serializers.ValidationError("Only admin users can log in here.")
