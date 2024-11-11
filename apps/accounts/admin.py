from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import SellerProfile, AdminProfile

# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from django.contrib.auth.models import Group

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    # fieldsets = UserAdmin.fieldsets + (
    #     (None, {'fields': ('groups',)}),
    # )

@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'company_name', 'is_verified']


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'department']


# class UserAdmin(BaseUserAdmin):
#     # Add 'groups' to the fields displayed when creating or editing a user
#     fieldsets = BaseUserAdmin.fieldsets + (
#         (None, {'fields': ('groups',)}),
#     )

# Unregister the original User admin and register the new one
# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)
# admin.site.register(Group)  # Ensure the Group model is registered
