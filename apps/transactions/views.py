from rest_framework import status, generics
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .models import BalanceIncreaseRequestModel, Sell
from .serializers import BalanceIncreaseRequestSerializer, ChargeCustomerSerializer
from ..accounts.permissions import IsSeller


class BalanceIncreaseRequestListCreateView(generics.ListCreateAPIView):
    queryset = BalanceIncreaseRequestModel.objects.all()
    serializer_class = BalanceIncreaseRequestSerializer

    def get_permissions(self):
        # Apply IsAdmin permission for GET requests
        if self.request.method == 'GET':
            permission_classes = [IsAdminUser]
        # Apply IsSeller permission for POST requests
        elif self.request.method == 'POST':
            permission_classes = [IsSeller]
        else:
            permission_classes = [IsAdminUser]

        return [permission() for permission in permission_classes]


class BalanceIncreaseRequestApprovalView(generics.UpdateAPIView):
    # TODO: add authentication/authorization
    queryset = BalanceIncreaseRequestModel.objects.filter(status=BalanceIncreaseRequestModel.STATUS_PENDING)
    serializer_class = BalanceIncreaseRequestSerializer
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        recharge: BalanceIncreaseRequestModel = self.get_object()
        action = kwargs.get("action")

        if action == BalanceIncreaseRequestModel.STATUS_ACCEPTED:
            recharge.approve()
        elif action == BalanceIncreaseRequestModel.STATUS_REJECTED:
            recharge.reject()
        else:
            return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(self.get_serializer(recharge).data)


class ChargeCustomerView(generics.CreateAPIView):
    queryset = Sell.objects.all()
    serializer_class = ChargeCustomerSerializer
    permission_classes = [IsSeller]
