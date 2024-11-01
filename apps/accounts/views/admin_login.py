from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.serializers.admin_login import AdminTokenObtainPairSerializer


class AdminTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = AdminTokenObtainPairSerializer
