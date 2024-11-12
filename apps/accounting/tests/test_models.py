from django.contrib.auth import get_user_model

from apps.accounting.models import AccountingEntry
from apps.accounts.tests.utils import AccountsTestUtils
from apps.transactions.models import BalanceIncreaseRequestModel, ChargeCustomerModel
from utils.api_test_case import ProjectAPITestCase as APITestCase

User = get_user_model()


class AccountingEntryModelTest(APITestCase):

    def setUp(self):
        self.user, self.seller = AccountsTestUtils.create_seller()

    def test_account_entry_recharge(self):
        # Create a recharge and approve it
        recharge = BalanceIncreaseRequestModel.objects.create(seller=self.seller, amount=50.00)
        recharge.approve()  # This should create an AccountingEntry

        # Verify AccountingEntry was created with correct values
        account_entry = AccountingEntry.objects.get(user=self.user, entry_type=AccountingEntry.RECHARGE)
        self.assertEqual(account_entry.amount, 50.00)
        self.assertEqual(account_entry.balance_after_entry, 150.00)
        self.assertEqual(account_entry.entry_type, 'recharge')

    def test_account_entry_sell(self):
        # Create a sell transaction
        customer_phone_number = "09999999999"
        ChargeCustomerModel.objects.create(seller=self.seller, phone_number=customer_phone_number, amount=20.00)

        # Verify AccountingEntry was created with correct values
        account_entry = AccountingEntry.objects.get(user=self.user, entry_type=AccountingEntry.SELL)
        self.assertEqual(account_entry.amount, -20.00)
        self.assertEqual(account_entry.balance_after_entry, 80.00)
        self.assertEqual(account_entry.entry_type, 'sell')
