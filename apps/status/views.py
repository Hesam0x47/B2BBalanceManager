from django.conf import settings
from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissions

from .models import StatusModel
from .permissions import CanChangeStatusOnlyPermission
from .serializers import StatusModelSerializer

rest_framework_settings = settings.REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"]


class StatusModelViewSet(viewsets.ModelViewSet):
    queryset = StatusModel.objects.all()
    serializer_class = StatusModelSerializer
    # todo: add DEFAULT_PERMISSION_CLASSES dynamically  to permission_classes
    permission_classes = [DjangoModelPermissions | CanChangeStatusOnlyPermission]
