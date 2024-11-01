from rest_framework import viewsets

from .models import AccountEntry
from .serializers import AccountEntrySerializer


class AccountEntryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AccountEntry.objects.all()
    serializer_class = AccountEntrySerializer
