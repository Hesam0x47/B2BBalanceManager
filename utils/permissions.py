from typing import Final

from django.conf import settings

rest_framework_settings = settings.REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"]


def get_default_permissions():
    """
    Helper function to retrieve default permission classes from settings.
    """
    permission_classes = []
    for perm_path in settings.REST_FRAMEWORK.get("DEFAULT_PERMISSION_CLASSES", []):
        module_path, class_name = perm_path.rsplit(".", 1)
        module = __import__(module_path, fromlist=[class_name])
        permission_classes.append(getattr(module, class_name))
    return permission_classes


def combine_permissions_with_or(permission_classes):
    """
    Dynamically combine default permissions with | operator
    """
    combined = permission_classes[0]
    for perm in permission_classes[1:]:
        combined |= perm
    return combined


default_permissions = get_default_permissions()
COMBINED_DEFAULT_PERMISSIONS: Final = combine_permissions_with_or(default_permissions)
