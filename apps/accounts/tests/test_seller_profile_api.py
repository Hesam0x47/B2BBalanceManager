from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.tests.utils import AccountsTestUtils
from utils.test_mixins import AdminAuthMixins, SellerUserMixins

User = get_user_model()


class SellerProfileAPITest(APITestCase, AdminAuthMixins, SellerUserMixins):
    def setUp(self):
        self.verified_seller_user, self.verified_seller_profile = AccountsTestUtils.create_seller(
            username="verified_seller",
            is_verified=True,
        )

        self.verified_seller_token, _ = self.login_seller(username="verified_seller")

        self.seller_list_url = reverse("seller-list")
        self.seller_retrieve_url = reverse("seller-retrieve", args=(self.verified_seller_user.username,))

        self.login_admin()
        return super().setUp()

    def test_list_sellers(self):
        response = self.client.get(self.seller_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.json())

        self.assertEqual(response.json()['count'], 1, msg=response.json())
        self.assertEqual(
            response.json()['results'][0].get('user', {}).get('username', ""),
            self.verified_seller_user.username, msg=response.json(),
        )

    def test_retrieve_seller(self):
        response = self.client.get(self.seller_retrieve_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.json())
        self.assertIn('user', response.json(), msg=response.json())
        self.assertIn('is_verified', response.json(), msg=response.json())
        self.assertIn('company_name', response.json(), msg=response.json())
        self.assertIn('balance', response.json(), msg=response.json())
        self.assertTrue(response.json().get('user', {}), msg=response.json())
