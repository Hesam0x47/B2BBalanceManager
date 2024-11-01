from django.urls import path

from .views import CreditIncreaseRequestListCreateView, CreditIncreaseRequestApprovalView

urlpatterns = [
    path('credit-increase-requests/', CreditIncreaseRequestListCreateView.as_view(), name='credit-increase-requests'),
    path('credit-increase-requests/<int:pk>/<str:action>/', CreditIncreaseRequestApprovalView.as_view(), name='credit-increase-requests-approval'),

    # TODO: add increase customers balance (charge sim-card)  API
]
