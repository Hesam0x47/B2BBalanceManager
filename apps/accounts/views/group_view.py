from django.contrib.auth.models import Group
from rest_framework import viewsets

from apps.accounts.serializers.group_serializer import GroupSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
