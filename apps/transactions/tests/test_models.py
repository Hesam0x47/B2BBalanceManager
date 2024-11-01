from django.core.exceptions import ValidationError
from django.db import transaction
from django.test import TestCase

from apps.accounts.models import User, SellerProfile
from apps.transactions.models import BalanceIncreaseRequestModel, Sell


class RechargeModelTest(TestCase):
    def setUp(self):
        self.seller_user = User.objects.create(username="seller", email="seller@example.com")
        self.seller = SellerProfile.objects.create(user=self.seller_user, balance=100.00)

    def test_recharge_pending(self):
        # Create a recharge that is pending
        recharge = BalanceIncreaseRequestModel.objects.create(seller=self.seller, amount=50.00)
        self.assertEqual(recharge.status, "pending")
        self.seller.refresh_from_db()
        self.assertEqual(self.seller.balance, 100.00)  # Balance shouldn't change for pending recharge

    def test_recharge_accepted(self):
        # Approve the recharge and check the balance update
        recharge = BalanceIncreaseRequestModel.objects.create(seller=self.seller, amount=50.00)
        recharge.approve()  # This should update the seller balance
        self.seller.refresh_from_db()
        self.assertEqual(recharge.status, "accepted")
        self.assertEqual(self.seller.balance, 150.00)

    def test_recharge_accepted_twice_recharge_once(self):
        # Approve the recharge and check the balance update
        recharge = BalanceIncreaseRequestModel.objects.create(seller=self.seller, amount=50.00)

        recharge.approve()  # This should update the seller balance
        self.seller.refresh_from_db()
        self.assertEqual(recharge.status, "accepted")
        self.assertEqual(self.seller.balance, 150.00)

        recharge.approve()  # This should not update the seller balance
        self.seller.refresh_from_db()
        self.assertEqual(recharge.status, "accepted")
        self.assertEqual(self.seller.balance, 150.00)

    def test_recharge_rejected(self):
        # Reject the recharge and ensure no balance update
        recharge = BalanceIncreaseRequestModel.objects.create(seller=self.seller, amount=50.00)
        recharge.reject()
        self.seller.refresh_from_db()
        self.assertEqual(recharge.status, "rejected")
        self.assertEqual(self.seller.balance, 100.00)  # Balance remains unchanged

    def test_recharge_rejected_twice_no_side_effect(self):
        # Reject the recharge and ensure no balance update
        recharge = BalanceIncreaseRequestModel.objects.create(seller=self.seller, amount=50.00)
        recharge.reject()
        self.seller.refresh_from_db()
        self.assertEqual(recharge.status, "rejected")
        self.assertEqual(self.seller.balance, 100.00)  # Balance remains unchanged

        recharge.reject()
        self.seller.refresh_from_db()
        self.assertEqual(recharge.status, "rejected")
        self.assertEqual(self.seller.balance, 100.00)  # Balance remains unchanged


class SellModelTest(TestCase):
    def setUp(self):
        self.seller_user = User.objects.create(username="seller", email="seller@example.com")
        self.seller = SellerProfile.objects.create(user=self.seller_user, balance=100.00)
        self.phone_number = "09999999999"

    def test_sell_transaction(self):
        # Test a valid sell transaction that reduces seller's balance
        sale = Sell.objects.create(seller=self.seller, phone_number=self.phone_number, amount=20.00)
        self.seller.refresh_from_db()
        self.assertEqual(sale.amount, 20.00)
        self.assertEqual(self.seller.balance, 80.00)  # Seller's balance is reduced

    def test_sell_transaction_insufficient_balance(self):
        # Test that an attempted sell with insufficient balance raises ValidationError
        with self.assertRaises(ValidationError):
            Sell.objects.create(seller=self.seller, phone_number=self.phone_number, amount=200.00)


class DoubleSpendingTest(TestCase):
    def setUp(self):
        self.seller_user = User.objects.create(username="seller", email="seller@example.com")
        self.seller = SellerProfile.objects.create(user=self.seller_user, balance=100.00)
        self.phone_number = "09999999999"

    def test_single_sell_transaction(self):
        Sell.objects.create(seller=self.seller, phone_number=self.phone_number, amount=20.00)
        self.seller.refresh_from_db()
        self.assertEqual(self.seller.balance, 80.00)

    def test_double_spending_prevention(self):
        # Simulate two simultaneous sell transactions to ensure insufficient balance is respected
        with transaction.atomic():
            Sell.objects.create(seller=self.seller, phone_number=self.phone_number, amount=60.00)
            with self.assertRaises(ValidationError):
                # This second transaction should fail due to insufficient funds
                Sell.objects.create(seller=self.seller, phone_number=self.phone_number, amount=60.00)
