from decimal import Decimal

from django.db import models
from django.db import transaction as db_transaction
from rest_framework.exceptions import ValidationError

from apps.accounting.models import AccountEntry
from apps.accounts.models import SellerProfile
from utils.helpers import acquire_thread_safe_lock


class ChargeCustomerModel(models.Model):
    seller = models.ForeignKey(SellerProfile, related_name="sales", on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # todo: CHANGE THIS FIELD TO PositiveIntegerField
    #  and limit it to 5000, 1000,20000,50000
    timestamp = models.DateTimeField(auto_now_add=True)

    def __process_charge_customer(self):
        with acquire_thread_safe_lock(f'sell-{self.seller.id}-lock'):
            # to prevent double-spending and race conditions
            seller = SellerProfile.objects.select_for_update().get(id=self.seller.id)
            if seller.balance < self.amount:
                raise ValidationError("Insufficient balance for this sale.")

            seller.balance -= Decimal(self.amount)
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
        self.__process_charge_customer()

        # we do not save anything, this model is just handling charge customers phone numbers
        # and keep the accounting information in accounting app
        # super().save(*args, **kwargs)

    def __str__(self):
        return f"Sell from {self.seller.user.username} to {self.phone_number} - ${self.amount}"


class BalanceIncreaseRequestModel(models.Model):
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

    @db_transaction.atomic
    def approve(self):
        # to prevent race conditions we use a thread-safe lock
        with acquire_thread_safe_lock(f'recharge-{self.seller.id}-lock'):
            if self.status == self.STATUS_ACCEPTED:
                # this guard prevents double-spending
                return

            self.status = self.STATUS_ACCEPTED
            self.save()
            self.__process_balance_increase()

    @db_transaction.atomic
    def reject(self):
        self.status = self.STATUS_REJECTED
        self.save()

    def __process_balance_increase(self):
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
