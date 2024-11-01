# accounting/tests/test_models.py
from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounting.models import AccountEntry
from apps.accounts.models import SellerProfile
from apps.transactions.models import BalanceIncreaseRequestModel, Sell

User = get_user_model()


class AccountEntryModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="seller", email="seller@example.com")
        self.seller = SellerProfile.objects.create(user=self.user, balance=100.00)

    def test_account_entry_recharge(self):
        # Create a recharge and approve it
        recharge = BalanceIncreaseRequestModel.objects.create(seller=self.seller, amount=50.00)
        recharge.approve()  # This should create an AccountEntry

        # Verify AccountEntry was created with correct values
        account_entry = AccountEntry.objects.get(user=self.user, entry_type=AccountEntry.RECHARGE)
        self.assertEqual(account_entry.amount, 50.00)
        self.assertEqual(account_entry.balance_after_entry, 150.00)
        self.assertEqual(account_entry.entry_type, 'recharge')

    def test_account_entry_sell(self):
        # Create a sell transaction
        customer_phone_number = "09999999999"
        Sell.objects.create(seller=self.seller, phone_number=customer_phone_number, amount=20.00)

        # Verify AccountEntry was created with correct values
        account_entry = AccountEntry.objects.get(user=self.user, entry_type=AccountEntry.SELL)
        self.assertEqual(account_entry.amount, -20.00)
        self.assertEqual(account_entry.balance_after_entry, 80.00)
        self.assertEqual(account_entry.entry_type, 'sell')
