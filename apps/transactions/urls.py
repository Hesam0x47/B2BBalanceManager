from django.urls import path
from .views import RechargeListCreateView, RechargeChangeStatusView

urlpatterns = [
    path('recharges/', RechargeListCreateView.as_view(), name='recharge-list-create'),
    path('recharges/<int:recharge_id>/<str:action>/', RechargeChangeStatusView.as_view(), name='recharge-change-status'),
]