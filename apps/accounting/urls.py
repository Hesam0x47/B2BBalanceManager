from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AccountingEntryViewSet

router = DefaultRouter()
router.register(r'entries', AccountingEntryViewSet, basename='accounting-entry')

urlpatterns = [
    path('', include(router.urls)),
]
