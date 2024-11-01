from rest_framework import generics
from rest_framework.permissions import AllowAny

from apps.accounts.serializers.seller_register import SellerRegistrationSerializer


class SellerRegistrationView(generics.CreateAPIView):
    serializer_class = SellerRegistrationSerializer
    permission_classes = [AllowAny]
