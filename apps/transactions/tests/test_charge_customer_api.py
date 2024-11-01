import random
from decimal import Decimal
from typing import Final

from django.contrib.auth import get_user_model
from django.db import models
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from apps.accounting.models import AccountEntry
from apps.accounts.tests.utils import AccountsTestUtils
from utils.test_mixins import SellerUserMixins, AdminAuthMixins

User = get_user_model()

INITIAL_BALANCE: Final[float] = 1000000.00


class BaseTestChargeCustomerAPI(APITestCase, SellerUserMixins, AdminAuthMixins):

    def setUp(self):
        self.charge_customer_url = reverse('charge-customer')

        # Create two sellers
        password = "sellerpass"
        self.tokens = []
        self.seller_users = []
        self.seller_profiles = []
        self.number_of_sellers = 2
        self.total_number_of_charges = 1000
        self.total_number_of_balance_increments = 0
        self.seller_current_balance = []
        for i in range(1, self.number_of_sellers + 1):
            self.seller_current_balance.append(INITIAL_BALANCE)

            seller_user, seller_profile = AccountsTestUtils.create_seller(
                username=f"seller{i}",
                password=password,
                balance=self.seller_current_balance[i - 1],
            )
            self.seller_users.append(seller_user)
            self.seller_profiles.append(seller_profile)
            token, _ = self.login_seller(username=seller_user.username, password=password)
            self.tokens.append(token)

    def charge_customer(self, amount):
        """Helper method to charge a customer for a specific amount with a specific seller token and random seller in payload."""
        # Randomly select a seller index
        seller_index = random.randint(0, self.number_of_sellers - 1)
        self.set_seller_authorization_token(self.tokens[seller_index])

        payload = {
            'seller': self.seller_users[seller_index].username,
            'amount': str(amount),
            'phone_number': f"09{random.randint(100000000, 999999999)}"
        }

        return self.client.post(self.charge_customer_url, payload)


class TestChargeCustomerAPI(BaseTestChargeCustomerAPI):
    def test_charge_customers_randomly(self):
        seller_totals = [0.0 for _ in range(self.number_of_sellers)]

        # Run too many random charge requests
        for _ in range(self.total_number_of_charges):
            amount = round(random.uniform(1, 50), 2)  # Random amount between 1 and 50
            response = self.charge_customer(amount)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

            # Update the total charged amount for the respective seller
            seller_index = int(str(response.data['seller']).replace("seller", ""))
            seller_totals[seller_index - 1] += amount

        # Refresh seller profiles to check final balances
        for i, seller_profile in enumerate(self.seller_profiles):
            seller_profile.refresh_from_db()
            expected_balance = Decimal(self.seller_current_balance[i] - seller_totals[i])
            self.assertAlmostEqual(seller_profile.balance, expected_balance, places=2)

            # Validate the AccountEntry records
            seller_entries_total = \
                AccountEntry.objects.filter(user=seller_profile.user, entry_type=AccountEntry.SELL).aggregate(
                    total=models.Sum('amount'))['total']
            self.assertAlmostEqual(-seller_entries_total, Decimal(seller_totals[i]), places=2)
