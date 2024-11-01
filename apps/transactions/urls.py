from django.urls import path

from .views import BalanceIncreaseRequestListCreateView, BalanceIncreaseRequestApprovalView, ChargeCustomerView

urlpatterns = [
    path('balance-increase-requests/', BalanceIncreaseRequestListCreateView.as_view(), name='balance-increase-requests'),
    path('balance-increase-requests/<int:pk>/<str:action>/', BalanceIncreaseRequestApprovalView.as_view(), name='balance-increase-requests-approval'),

    # TODO: add increase customers balance (charge sim-card)  API
    path('charge-customer/', ChargeCustomerView.as_view(), name='charge-customer'),
]
