from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.serializers.seller_login import SellerLoginSerializer


class SellerLoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = SellerLoginSerializer
