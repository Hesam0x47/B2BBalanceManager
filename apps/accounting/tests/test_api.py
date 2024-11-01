from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounting.models import AccountEntry
from apps.accounts.models import SellerProfile
from apps.transactions.models import BalanceIncreaseRequestModel, Sell
from utils.test_mixins import AdminAuthMixins

User = get_user_model()


class AccountEntryAPITest(APITestCase, AdminAuthMixins):

    def setUp(self):
        # Set up a seller and authenticate
        self.user = User.objects.create_user(username="seller", password="password", email="seller@example.com")
        self.client.login(username="seller", password="password")

        self.seller = SellerProfile.objects.create(user=self.user, balance=100.00)

        self.login()
        self.set_admin_authorization()

    def test_account_entry_list(self):
        # Create a recharge and approve it
        recharge = BalanceIncreaseRequestModel.objects.create(seller=self.seller, amount=50.00)
        recharge.approve()  # This should create an AccountEntry

        url = reverse('accountentry-list')  # List endpoint
        response = self.client.get(url)

        # Verify the API returns the correct account entry data
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.json())
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['entry_type'], 'recharge')
        self.assertEqual(response.data[0]['amount'], "50.00")
        self.assertEqual(response.data[0]['balance_after_entry'], "150.00")

    def test_account_entry_detail(self):
        customer_phone_number = "09999999999"

        Sell.objects.create(seller=self.seller, phone_number=customer_phone_number, amount=20.00)

        # Get the created AccountEntry for the sell transaction
        account_entry = AccountEntry.objects.get(user=self.user, entry_type=AccountEntry.SELL)
        url = reverse('accountentry-detail', args=[account_entry.id])  # Detail endpoint
        response = self.client.get(url)

        # Verify the API returns the correct account entry data
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.json())
        self.assertEqual(response.data['entry_type'], 'sell')
        self.assertEqual(response.data['amount'], "-20.00")
        self.assertEqual(response.data['balance_after_entry'], "80.00")
