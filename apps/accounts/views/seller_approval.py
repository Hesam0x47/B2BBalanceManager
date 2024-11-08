from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from apps.accounts.models import SellerProfile
from apps.accounts.serializers.seller_approval import SellerApprovalSerializer


class SellerApprovalView(generics.UpdateAPIView):
    queryset = SellerProfile.objects.all()
    serializer_class = SellerApprovalSerializer
    permission_classes = [IsAdminUser]

    def update(self, request, *args, **kwargs):
        seller_profile = self.get_object()
        serializer = self.get_serializer(seller_profile, data={}, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({"detail": "Seller has been approved."}, status=status.HTTP_200_OK)
