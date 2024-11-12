from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from utils.api_test_case import ProjectAPITestCase as APITestCase

from apps.accounting.models import AccountingEntry
from apps.accounts.tests.utils import AccountsTestUtils
from apps.transactions.models import BalanceIncreaseRequestModel, ChargeCustomerModel
from utils.test_mixins import AdminAuthMixins

User = get_user_model()


class AccountingEntryAPITest(APITestCase, AdminAuthMixins):

    def setUp(self):
        # Set up a seller and authenticate
        self.seller_user, self.seller = AccountsTestUtils.create_seller(username="seller", password="password",
                                                                        email="seller@example.com")

        self.client.login(username="seller", password="password")

        self.login_admin()

    def test_account_entry_list_balance_accepted(self):
        # Create a recharge and approve it
        recharge = BalanceIncreaseRequestModel.objects.create(seller=self.seller, amount=50.00)
        recharge.approve()  # This should create an AccountingEntry

        url = reverse('accounting-entry-list')  # List endpoint
        response = self.client.get(url)

        # Verify the API returns the correct account entry data
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.json())
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['entry_type'], 'recharge')
        self.assertEqual(response.data['results'][0]['amount'], "50.00")
        self.assertEqual(response.data['results'][0]['balance_after_entry'], "150.00")

    def test_account_entry_list_balance_rejected(self):
        # Create a recharge and approve it
        recharge = BalanceIncreaseRequestModel.objects.create(seller=self.seller, amount=50.00)
        recharge.reject()  # This should not create an AccountingEntry

        url = reverse('accounting-entry-list')  # List endpoint
        response = self.client.get(url)

        # Verify the API returns the correct account entry data
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.json())
        self.assertEqual(len(response.data['results']), 0)

    def test_account_entry_detail(self):
        customer_phone_number = "09999999999"

        ChargeCustomerModel.objects.create(seller=self.seller, phone_number=customer_phone_number, amount=20.00)

        # Get the created AccountingEntry for the sell transaction
        account_entry = AccountingEntry.objects.get(user=self.seller_user, entry_type=AccountingEntry.SELL)
        url = reverse('accounting-entry-detail', args=[account_entry.id])  # Detail endpoint
        response = self.client.get(url)

        # Verify the API returns the correct account entry data
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.json())
        self.assertEqual(response.data['entry_type'], 'sell')
        self.assertEqual(response.data['amount'], "-20.00")
        self.assertEqual(response.data['balance_after_entry'], "80.00")
