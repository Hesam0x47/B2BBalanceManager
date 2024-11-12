from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StatusModelViewSet

router = DefaultRouter()
router.register(r'status', StatusModelViewSet, basename='status-api')

urlpatterns = [
    path('', include(router.urls)),
]
