from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import SellerProfile

User = get_user_model()


class SellerRegistrationAPITest(APITestCase):
    def setUp(self):
        # URL for the seller registration endpoint
        self.url = reverse("seller-register")
        # Registration data for a new seller
        self.data = {
            "username": "seller1",
            "email": "seller@example.com",
            "password": "sellerpassword",
            "password2": "sellerpassword",
            "company_name": "sellercompany"
        }

    def test_seller_registration_success(self):
        # Send POST request to register a new seller
        response = self.client.post(self.url, self.data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check if the User instance is created
        user = User.objects.get(username="seller1")
        self.assertEqual(user.email, "seller@example.com")

        # Check if the SellerProfile instance is created and linked to the user
        seller_profile = SellerProfile.objects.get(user=user)
        self.assertEqual(seller_profile.company_name, "sellercompany")
        self.assertFalse(seller_profile.is_verified)  # Check if the default is_verified is False

    def test_seller_registration_password_mismatch(self):
        # Test with mismatched passwords
        self.data["password2"] = "differentpassword"
        response = self.client.post(self.url, self.data, format="json")

        # Ensure registration fails with a 400 response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)  # Check if the error message is about password mismatch

    def test_seller_registration_missing_company_name(self):
        # Test with missing company_name
        del self.data["company_name"]
        response = self.client.post(self.url, self.data, format="json")

        # Ensure registration fails with a 400 response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, msg=response.json())
        self.assertIn("company_name", response.data)  # Check if the error message is about missing company_name
