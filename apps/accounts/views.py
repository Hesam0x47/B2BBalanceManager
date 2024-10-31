from rest_framework import generics

from .models import SellerProfile, CustomerProfile, AdminProfile
from .serializers import (
    SellerProfileSerializer,
    # CustomerProfileSerializer,
    # AdminProfileSerializer,
)


class SellerProfileListCreateView(generics.ListCreateAPIView):
    queryset = SellerProfile.objects.all()
    serializer_class = SellerProfileSerializer


# class CustomerProfileListCreateView(generics.ListCreateAPIView):
#     queryset = CustomerProfile.objects.all()
#     serializer_class = CustomerProfileSerializer
#
#
# class AdminProfileListCreateView(generics.ListCreateAPIView):
#     queryset = AdminProfile.objects.all()
#     serializer_class = AdminProfileSerializer
