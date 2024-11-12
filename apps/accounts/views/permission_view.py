from django.contrib.auth.models import Permission
from rest_framework import viewsets

from apps.accounts.serializers.permission_serializer import PermissionSerializer


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
