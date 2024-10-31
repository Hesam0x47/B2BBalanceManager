from django.urls import path
from .views import (
    SellerProfileListCreateView,
    # CustomerProfileListCreateView,
    # AdminProfileListCreateView,
)

urlpatterns = [
    path('sellers/', SellerProfileListCreateView.as_view(), name='seller-list-create'),
    # path('customers/', CustomerProfileListCreateView.as_view(), name='customer-list-create'),
    # path('admins/', AdminProfileListCreateView.as_view(), name='admin-list-create'),
]
