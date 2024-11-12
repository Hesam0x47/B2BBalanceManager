from django.db import transaction
from utils.api_test_case import ProjectAPITestCase as APITestCase
from rest_framework.exceptions import ValidationError

from apps.accounts.tests.utils import AccountsTestUtils
from apps.transactions.models import BalanceIncreaseRequestModel, ChargeCustomerModel


class RechargeModelTest(APITestCase):
    def setUp(self):
        self.seller_user, self.seller_profile = AccountsTestUtils.create_seller()

    def test_recharge_pending(self):
        # Create a recharge that is pending
        recharge = BalanceIncreaseRequestModel.objects.create(seller=self.seller_profile, amount=50.00)
        self.assertEqual(recharge.status, "pending")
        self.seller_profile.refresh_from_db()
        self.assertEqual(self.seller_profile.balance, 100.00)  # Balance shouldn't change for pending recharge

    def test_recharge_accepted(self):
        # Approve the recharge and check the balance update
        recharge = BalanceIncreaseRequestModel.objects.create(seller=self.seller_profile, amount=50.00)
        recharge.approve()  # This should update the seller balance
        self.seller_profile.refresh_from_db()
        self.assertEqual(recharge.status, "accepted")
        self.assertEqual(self.seller_profile.balance, 150.00)

    def test_recharge_accepted_twice_recharge_once(self):
        # Approve the recharge and check the balance update
        recharge = BalanceIncreaseRequestModel.objects.create(seller=self.seller_profile, amount=50.00)

        recharge.approve()  # This should update the seller balance
        self.seller_profile.refresh_from_db()
        self.assertEqual(recharge.status, "accepted")
        self.assertEqual(self.seller_profile.balance, 150.00)

        recharge.approve()  # This should not update the seller balance
        self.seller_profile.refresh_from_db()
        self.assertEqual(recharge.status, "accepted")
        self.assertEqual(self.seller_profile.balance, 150.00)

    def test_recharge_rejected(self):
        # Reject the recharge and ensure no balance update
        recharge = BalanceIncreaseRequestModel.objects.create(seller=self.seller_profile, amount=50.00)
        recharge.reject()
        self.seller_profile.refresh_from_db()
        self.assertEqual(recharge.status, "rejected")
        self.assertEqual(self.seller_profile.balance, 100.00)  # Balance remains unchanged

    def test_recharge_rejected_twice_no_side_effect(self):
        # Reject the recharge and ensure no balance update
        recharge = BalanceIncreaseRequestModel.objects.create(seller=self.seller_profile, amount=50.00)
        recharge.reject()
        self.seller_profile.refresh_from_db()
        self.assertEqual(recharge.status, "rejected")
        self.assertEqual(self.seller_profile.balance, 100.00)  # Balance remains unchanged

        recharge.reject()
        self.seller_profile.refresh_from_db()
        self.assertEqual(recharge.status, "rejected")
        self.assertEqual(self.seller_profile.balance, 100.00)  # Balance remains unchanged


class SellModelTest(APITestCase):
    def setUp(self):
        self.seller_user, self.seller_profile = AccountsTestUtils.create_seller()

        self.phone_number = "09999999999"

    def test_sell_transaction(self):
        # Test a valid sell transaction that reduces seller's balance
        sale = ChargeCustomerModel.objects.create(seller=self.seller_profile, phone_number=self.phone_number, amount=20.00)
        self.seller_profile.refresh_from_db()
        self.assertEqual(sale.amount, 20.00)
        self.assertEqual(self.seller_profile.balance, 80.00)  # Seller's balance is reduced

    def test_sell_transaction_insufficient_balance(self):
        # Test that an attempted sell with insufficient balance raises ValidationError
        with self.assertRaises(ValidationError):
            ChargeCustomerModel.objects.create(seller=self.seller_profile, phone_number=self.phone_number, amount=200.00)


class DoubleSpendingTest(APITestCase):
    def setUp(self):
        self.seller_user, self.seller_profile = AccountsTestUtils.create_seller()
        self.phone_number = "09999999999"

    def test_single_sell_transaction(self):
        ChargeCustomerModel.objects.create(seller=self.seller_profile, phone_number=self.phone_number, amount=20.00)
        self.seller_profile.refresh_from_db()
        self.assertEqual(self.seller_profile.balance, 80.00)

    def test_double_spending_prevention(self):
        # Simulate two simultaneous sell transactions to ensure insufficient balance is respected
        with transaction.atomic():
            ChargeCustomerModel.objects.create(seller=self.seller_profile, phone_number=self.phone_number, amount=60.00)
            with self.assertRaises(ValidationError):
                # This second transaction should fail due to insufficient funds
                ChargeCustomerModel.objects.create(seller=self.seller_profile, phone_number=self.phone_number, amount=60.00)
