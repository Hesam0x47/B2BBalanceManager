import random
from decimal import Decimal
from typing import List

from django.contrib.auth import get_user_model
from django.db import models
from rest_framework import status

from apps.accounting.models import AccountingEntry
from apps.transactions.tests.test_charge_customer_api import BaseTestChargeCustomerAPI
from apps.transactions.tests.utils import IncreaseBalanceTestMixins

User = get_user_model()


class TestCompleteUserStoryAPI(BaseTestChargeCustomerAPI, IncreaseBalanceTestMixins):

    def test_charge_1000_customers_2_sellers_10_balance_increase(self):
        self.total_number_of_balance_increments = 10

        total_sells = [0.0 for _ in range(self.number_of_sellers)]
        random_increase_balance_where: List[int] = []
        for _ in range(self.total_number_of_balance_increments):
            rand_number = 0
            while rand_number not in random_increase_balance_where:
                rand_number = random.randint(0, self.total_number_of_charges - 1)
                random_increase_balance_where.append(rand_number)

        # Run too many random charge requests
        for i in range(self.total_number_of_charges):

            amount = round(random.uniform(1, 50), 2)  # Random amount between 1 and 50
            seller_index, response = self.charge_customer(amount)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

            # Update the total charged amount for the respective seller
            total_sells[seller_index] += amount

            if i in random_increase_balance_where:
                amount = round(random.uniform(1, 10000), 2)
                response = self.increase_balance(amount=str(amount))
                pk = response.data['id']
                self.login_admin()
                self.approve_increase_balance_request(pk)
                self.seller_current_balance[seller_index] += amount

                # Refresh seller profiles to check final balances
        for i, seller_profile in enumerate(self.seller_profiles):
            seller_profile.refresh_from_db()
            expected_balance = Decimal(self.seller_current_balance[i] - total_sells[i])
            self.assertAlmostEqual(seller_profile.balance, expected_balance, places=2)

            # Validate the AccountingEntry records
            seller_entries_total = \
                AccountingEntry.objects.filter(user=seller_profile.user, entry_type=AccountingEntry.SELL).aggregate(
                    total=models.Sum('amount'))['total']
            self.assertAlmostEqual(-seller_entries_total, Decimal(total_sells[i]), places=2)
