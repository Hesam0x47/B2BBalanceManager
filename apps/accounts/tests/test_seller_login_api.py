from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixins import SellerUserMixins

User = get_user_model()


class SellerLoginAPITest(APITestCase, SellerUserMixins):
    def setUp(self):
        # URL for the seller login endpoint
        self.login_url = reverse("seller-login")

        # Create a verified seller
        self.verified_seller_user, self.verified_seller_profile = self.create_seller_profile(
            username="verified_seller",
            is_verified=True,
        )

        # Create an unverified seller
        self.unverified_seller_user, self.unverified_seller_profile = self.create_seller_profile(
            username="unverified_seller",
            is_verified=False,
        )

        # Create a non-seller user
        self.non_seller_user = User.objects.create_user(username="regular_user", password="password123")

    def test_verified_seller_login_success(self):
        # Login attempt with verified seller credentials
        _, response = self.login_seller(username=self.verified_seller_user.username)

        # Check if login is successful and JWT tokens are returned
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.json())
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_unverified_seller_login_failure(self):
        # Login attempt with unverified seller credentials
        _, response = self.login_seller(username=self.unverified_seller_user.username,
                                        expected_status_code=status.HTTP_400_BAD_REQUEST)

        # Check if login fails due to unverified account
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Your account is not verified", response.data["non_field_errors"][0])

    def test_non_seller_login_failure(self):
        # Login attempt with regular non-seller user credentials
        response = self.client.post(
            self.login_url, {"username": "regular_user", "password": "password123"},
            format="json",
        )

        # Check if login fails due to missing seller profile
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Your account is not verified", response.data["non_field_errors"][0])
