from django.urls import path
from rest_framework.routers import DefaultRouter

from .views.admin_login import AdminTokenObtainPairView
from .views.group_view import GroupViewSet
from .views.permission_view import PermissionViewSet
from .views.seller_login import SellerLoginView
from .views.seller_profile import SellerProfileListView, SellerProfileRetrieveView
from .views.seller_registration import SellerRegistrationView
from .views.seller_verification import SellerVerificationView

urlpatterns = [
    path('admin/login/', AdminTokenObtainPairView.as_view(), name='admin-login'),
    path('admin/verify-seller/<str:user__username>/', SellerVerificationView.as_view(), name='verify-seller'),
    # Admin-only URL

    path("seller/register/", SellerRegistrationView.as_view(), name="seller-register"),
    path("seller/login/", SellerLoginView.as_view(), name="seller-login"),
    path('sellers/', SellerProfileListView.as_view(), name='seller-list'),
    path('sellers/<str:user__username>/', SellerProfileRetrieveView.as_view(), name='seller-retrieve'),

    # todo: add logout api for admin and seller
]

router = DefaultRouter()
router.register(r'groups', GroupViewSet)
router.register(r'permissions', PermissionViewSet)


urlpatterns += router.urls