from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class CanChangeStatusOnlyPermission(permissions.BasePermission):
    """
    Custom permission to allow only users with the 'can_change_status_only' permission
    to update the 'status' field.
    """

    def has_permission(self, request, view):
        # Check if the user has the 'can_change_status_only' permission
        if not request.user.has_perm('status.can_change_status_only'):
            return False

        return True

    def has_object_permission(self, request, view, obj):
        # Allow PATCH or PUT only if the request data contains only the 'status' field
        if request.method in ('PATCH', 'PUT'):
            requested_fields = request.data.keys()
            if 'status' in requested_fields and len(requested_fields) == 1:
                return True
            else:
                raise PermissionDenied("You are only allowed to update the 'status' field.")

        return False
