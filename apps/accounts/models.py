from typing import Final

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ADMIN = 'admin'
    SELLER = 'seller'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (SELLER, 'Seller'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.role})"


class SellerProfile(models.Model):
    RELATED_NAME: Final[str] = 'seller_profile'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name=RELATED_NAME)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    is_verified = models.BooleanField(default=False)  # TODO: add new api for seller verification

    def __str__(self):
        return f"Seller: {self.user.username}"


class CustomerProfile(models.Model):
    # we do not need user field because the application is B2B and there is no end-user
    # user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone_number = models.CharField(max_length=15, unique=True)  # Unique identifier for customers in B2B

    def __str__(self):
        return f"Customer: {self.phone_number}"


class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    department = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Admin: {self.user.username}"
