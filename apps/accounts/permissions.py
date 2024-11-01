from rest_framework import permissions
from .models import SellerProfile

class IsSeller(permissions.BasePermission):
    """
    Custom permission to only allow access to users with a SellerProfile.
    """

    def has_permission(self, request, view):
        # Ensure the user is authenticated and has an associated SellerProfile
        return request.user.is_authenticated and hasattr(request.user, SellerProfile.RELATED_NAME)
