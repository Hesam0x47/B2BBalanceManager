from django.core.exceptions import ValidationError
from django.db import transaction
from django.test import TestCase

from apps.accounts.models import User, SellerProfile
from apps.transactions.models import Transaction


class TransactionModelTest(TestCase):

    def setUp(self):
        self.seller_username = "seller"
        self.seller_user = User.objects.create(username=self.seller_username, email="seller@example.com")
        self.seller = SellerProfile.objects.create(user=self.seller_user, balance=100.00)

    def test_transaction_sell(self):
        transaction_sell = Transaction.objects.create(
            seller=self.seller,
            transaction_type=Transaction.SELL,
            amount=20.00,
        )
        self.seller.refresh_from_db()
        self.assertEqual(transaction_sell.transaction_type, "sell")
        self.assertEqual(self.seller.balance, 80.00)

    def test_transaction_recharge(self):
        transaction_recharge = Transaction.objects.create(
            seller=self.seller,
            transaction_type=Transaction.RECHARGE,
            amount=50.00,
        )
        self.seller.refresh_from_db()
        self.assertEqual(transaction_recharge.transaction_type, "recharge")
        self.assertEqual(self.seller.balance, 150.00)


class DoubleSpendingTest(TestCase):

    def setUp(self):
        self.seller_username = "seller"
        self.seller_user = User.objects.create(username=self.seller_username, email="seller@example.com")
        self.seller = SellerProfile.objects.create(user=self.seller_user, balance=100.00)

    def test_single_transaction(self):
        Transaction.objects.create(
            seller=self.seller,
            transaction_type=Transaction.SELL,
            amount=20.00,
        )
        self.seller.refresh_from_db()
        self.assertEqual(self.seller.balance, 80.00)

    def test_double_spending_prevention(self):
        # Simulate two simultaneous sell transactions that exceed balance
        with transaction.atomic():
            Transaction.objects.create(
                seller=self.seller,
                transaction_type=Transaction.SELL,
                amount=60.00,
            )
            with self.assertRaises(ValidationError):
                # This second transaction should fail due to insufficient funds
                Transaction.objects.create(
                    seller=self.seller,
                    transaction_type=Transaction.SELL,
                    amount=60.00,
                )
