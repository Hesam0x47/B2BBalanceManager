from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # Add any common fields here if needed
    pass


# accounts/models.py
class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Seller: {self.user.username}"


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    address = models.TextField(blank=True, null=True)
    loyalty_points = models.IntegerField(default=0)

    def __str__(self):
        return f"Customer: {self.user.username}"


class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    department = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Admin: {self.user.username}"

# class Seller(AbstractUser):
#     email = models.EmailField(unique=True, null=False, blank=False)
#     balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
#     company_name = models.CharField(max_length=255, blank=True, null=True)
#     is_verified = models.BooleanField(default=True)  # TODO: add new api for seller verification
#
#     def __str__(self):
#         return f"{self.username} - Balance: {self.balance}"
