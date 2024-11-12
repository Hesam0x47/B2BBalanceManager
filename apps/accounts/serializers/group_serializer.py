from django.contrib.auth.models import Group
from rest_framework import serializers

from apps.accounts.serializers.permission_serializer import PermissionSerializer


class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']
