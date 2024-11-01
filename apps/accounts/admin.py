from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, SellerProfile, AdminProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'company_name', 'is_verified']


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'department']
