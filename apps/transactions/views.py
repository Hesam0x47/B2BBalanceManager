from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .models import Recharge
from .serializers import RechargeSerializer


class RechargeListCreateView(generics.ListCreateAPIView):
    queryset = Recharge.objects.all()
    serializer_class = RechargeSerializer


class RechargeChangeStatusView(generics.UpdateAPIView):
    # TODO: add authentication/authorization
    permission_classes = [IsAdminUser]
    queryset = Recharge.objects.filter(status=Recharge.STATUS_PENDING)
    serializer_class = RechargeSerializer
    lookup_field = 'pk'
    def update(self, request, *args, **kwargs):
        recharge:Recharge = self.get_object()
        action = kwargs.get("action")

        if action == Recharge.STATUS_ACCEPTED:
            recharge.approve()
        elif action == Recharge.STATUS_REJECTED:
            recharge.reject()
        else:
            return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(self.get_serializer(recharge).data)

    # def post(self, request, recharge_id, action):
    #     recharge = get_object_or_404(Recharge, id=recharge_id)
    #
    #     if recharge.status != Recharge.STATUS_PENDING:
    #         return Response({"detail": f"Recharge is already {recharge.status}."}, status=status.HTTP_400_BAD_REQUEST)
    #
    #     recharge.process_recharge(**self.kwargs)
    #
    #     serializer = RechargeSerializer(recharge)
    #     return Response(serializer.data, status=status.HTTP_200_OK)
