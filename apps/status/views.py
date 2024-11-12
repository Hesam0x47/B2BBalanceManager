from rest_framework import viewsets

from utils.permissions import COMBINED_DEFAULT_PERMISSIONS
from .models import StatusModel
from .permissions import CanChangeStatusOnlyPermission
from .serializers import StatusModelSerializer


class StatusModelViewSet(viewsets.ModelViewSet):
    queryset = StatusModel.objects.all()
    serializer_class = StatusModelSerializer

    permission_classes = [COMBINED_DEFAULT_PERMISSIONS | CanChangeStatusOnlyPermission]
