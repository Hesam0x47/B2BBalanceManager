from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AccountEntryViewSet

router = DefaultRouter()
router.register(r'entries', AccountEntryViewSet, basename='accountentry')

urlpatterns = [
    path('', include(router.urls)),
]
