from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import AccountEntry
from .serializers import AccountEntrySerializer


class AccountEntryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AccountEntry.objects.all()
    serializer_class = AccountEntrySerializer
    # permission_classes = [IsAuthenticated]
