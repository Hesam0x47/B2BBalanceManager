from django.urls import path

from .views import RechargeListCreateView, RechargeChangeStatusView

urlpatterns = [
    path('recharges/', RechargeListCreateView.as_view(), name='recharge-list-create'),
    path('recharges/<int:pk>/<str:action>/', RechargeChangeStatusView.as_view(), name='recharge-change-status'),

    # TODO: add increase customers balance (charge sim-card)  API
]
