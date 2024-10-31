from django.core.exceptions import ValidationError
from django.db import transaction
from django.test import TestCase

from apps.transactions.models import Transaction, Seller


class SellerModelTest(TestCase):

    def setUp(self):
        self.seller = Seller.objects.create(name="Test Seller", email="seller@example.com", balance=100.00)

    def test_create_seller(self):
        self.assertEqual(self.seller.name, "Test Seller")
        self.assertEqual(self.seller.email, "seller@example.com")
        self.assertEqual(self.seller.balance, 100.00)

    def test_delete_seller(self):
        self.assertEqual(Seller.objects.all().count(), 1)
        self.seller.delete()
        self.assertEqual(Seller.objects.all().count(), 0)

    def test_update_seller_balance(self):
        self.assertEqual(self.seller.balance, 100.00)
        self.seller.balance = 200.00
        self.seller.save()
        self.assertEqual(self.seller.balance, 200.00)
        self.seller.balance = 3000.00
        self.seller.save()
        self.assertEqual(self.seller.balance, 3000.00)

    def test_update_seller_name(self):
        self.seller.name = "Test Seller New"
        self.seller.save()
        self.assertEqual(self.seller.name, "Test Seller New")

    def test_update_seller_email(self):
        self.seller.email = "seller_new@example.com"
        self.seller.save()
        self.assertEqual(self.seller.email, "seller_new@example.com")


class TransactionModelTest(TestCase):

    def setUp(self):
        self.seller = Seller.objects.create(name="Test Seller", email="seller@example.com", balance=100.00)

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
        self.seller = Seller.objects.create(name="Test Seller", balance=100.00)

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
