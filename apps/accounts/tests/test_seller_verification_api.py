from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from utils.api_test_case import ProjectAPITestCase as APITestCase

from apps.accounts.tests.utils import AccountsTestUtils
from utils.test_mixins import AdminAuthMixins, SellerUserMixins

User = get_user_model()


class SellerVerificationAPITest(APITestCase, AdminAuthMixins, SellerUserMixins):
    def setUp(self):
        self.verified_seller_user, self.verified_seller_profile = AccountsTestUtils.create_seller(
            username="verified_seller",
            is_verified=True,
        )
        self.non_verified_seller_user, self.non_verified_seller_profile = AccountsTestUtils.create_seller(
            username="non_verified_seller",
            is_verified=False,
        )

        self.verified_seller_token, _ = self.login_seller(username="verified_seller")

        self.verify_seller_url = reverse("verify-seller", args=[self.non_verified_seller_profile.user.username])
        return super().setUp()

    def test_verify_seller_as_admin(self):
        self.login_admin()

        # Admin attempts to verify the seller
        response = self.client.patch(self.verify_seller_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.json())

        self.non_verified_seller_profile.refresh_from_db()
        self.assertTrue(self.non_verified_seller_profile.is_verified)

    def test_verify_seller_as_non_admin(self):
        self.login_seller(self.verified_seller_user.username)
        self.set_seller_authorization_token(self.verified_seller_token)

        # Seller attempts to verify themselves, which should fail
        response = self.client.patch(self.verify_seller_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, msg=response.json())

        # Ensure the seller is still not verified
        self.non_verified_seller_profile.refresh_from_db()
        self.assertFalse(self.non_verified_seller_profile.is_verified)

    def test_verify_seller_without_authentication(self):
        response = self.client.patch(self.verify_seller_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, msg=response.json())

        # Ensure the seller is still not verified
        self.non_verified_seller_profile.refresh_from_db()
        self.assertFalse(self.non_verified_seller_profile.is_verified)
