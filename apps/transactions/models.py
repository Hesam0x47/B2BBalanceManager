from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.db import transaction as db_transaction
from django.db.models import F

from apps.accounting.models import AccountEntry
from apps.accounts.models import SellerProfile
from apps.accounts.models import SellerProfile, CustomerProfile
from utils.helpers import acquire_thread_safe_lock


#
# class Transaction(models.Model):
#     SELL = 'sell'
#     RECHARGE = 'recharge'
#     TRANSACTION_TYPES = [
#         (SELL, 'Sell'),
#         (RECHARGE, 'Recharge'),
#     ]
#
#     seller = models.ForeignKey(SellerProfile, related_name="transactions", on_delete=models.CASCADE)
#     transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     timestamp = models.DateTimeField(auto_now_add=True)
#
#     @transaction.atomic
#     def save(self, *args, **kwargs):
#         """
#         Saves the transaction object to the database
#
#         Use atomic transaction to prevent double spending
#         :param args:
#         :param kwargs:
#         :return:
#         """
#         with acquire_thread_safe_lock(f'seller-{self.seller.id}-lock'):
#             # Lock the seller row to prevent concurrent updates
#             seller = SellerProfile.objects.select_for_update().get(id=self.seller.id)
#
#             if self.transaction_type == self.SELL:
#                 # Ensure there's enough balance to perform the transaction
#                 if seller.balance < self.amount:
#                     raise ValidationError("Insufficient balance for this transaction.")
#                 seller.balance = F('balance') - self.amount
#             elif self.transaction_type == self.RECHARGE:
#                 seller.balance = F('balance') + self.amount
#
#             # Save the balance update
#             seller.save()
#             super().save(*args, **kwargs)
#
#     def __str__(self):
#         return f"{self.seller.user.username} - {self.transaction_type.capitalize()} - ${self.amount}"
#


class Sell(models.Model):
    seller = models.ForeignKey(SellerProfile, related_name="sales", on_delete=models.CASCADE)
    customer = models.ForeignKey(CustomerProfile, related_name="purchases", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __process_sale(self):
        with acquire_thread_safe_lock(f'sell-{self.seller.id}-lock'):
            # to prevent double-spending and race conditions
            seller = SellerProfile.objects.select_for_update().get(id=self.seller.id)
            if seller.balance < self.amount:
                raise ValidationError("Insufficient balance for this sale.")

            seller.balance -=  Decimal(self.amount)
            seller.save()

        # Log the sale in AccountEntry
        AccountEntry.objects.create(
            user=seller.user,
            entry_type='sell',
            amount=-self.amount,
            balance_after_entry=seller.balance
        )

    @db_transaction.atomic
    def save(self, *args, **kwargs):
        self.__process_sale()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sell from {self.seller.user.username} to {self.customer.user.username} - ${self.amount}"


class CreditIncreaseRequestModel(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    seller = models.ForeignKey(SellerProfile, related_name="recharges", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)

    def approve(self):
        # to prevent race conditions we use a thread-safe lock
        with acquire_thread_safe_lock(f'recharge-{self.seller.id}-lock'):
            if self.status == self.STATUS_ACCEPTED:
                # this guard prevents double-spending
                return

            self.status = self.STATUS_ACCEPTED
            self.save()
            self.__process_recharge()

    def reject(self):
        self.status = self.STATUS_REJECTED
        self.save()

    def __process_recharge(self):
        if self.status == self.STATUS_ACCEPTED:
            self.seller.balance += self.amount
            self.seller.save()

            # Log the recharge in AccountEntry
            AccountEntry.objects.create(
                user=self.seller.user,
                entry_type='recharge',
                amount=self.amount,
                balance_after_entry=self.seller.balance
            )

    @db_transaction.atomic
    def save(self, *args, **kwargs):
        return super().save()

    def __str__(self):
        return f"Recharge for {self.seller.user.username} - ${self.amount} - {self.status.capitalize()}"
