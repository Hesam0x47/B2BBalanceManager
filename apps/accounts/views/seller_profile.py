from rest_framework import generics

from apps.accounts.models import SellerProfile
from apps.accounts.serializers.seller_profile import SellerProfileSerializer


class SellerProfileListView(generics.ListAPIView):
    queryset = SellerProfile.objects.all()
    serializer_class = SellerProfileSerializer


class SellerProfileRetrieveView(generics.RetrieveAPIView):
    queryset = SellerProfile.objects.all()
    serializer_class = SellerProfileSerializer
    lookup_field = "user__username"

