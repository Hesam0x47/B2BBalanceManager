from django.db import models
from django.db import transaction as db_transaction
from django.db.models import F
from rest_framework.exceptions import ValidationError

from apps.accounting.models import AccountEntry
from apps.accounts.models import SellerProfile
from utils.helpers import acquire_thread_safe_lock



class ChargeCustomerModel(models.Model):
    seller = models.ForeignKey(SellerProfile, related_name="charge_customer", on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # todo: CHANGE THIS FIELD TO PositiveIntegerField
                                                                   #  and limit it to 5000, 1000,20000,50000
    timestamp = models.DateTimeField(auto_now_add=True)

    def __process_charge_customer(self):
        seller_lock_name = f"seller-{self.seller.id}-lock"  # Lock per seller

        with acquire_thread_safe_lock(seller_lock_name):
            # to prevent double-spending and race conditions
            self.seller.refresh_from_db()
            if self.seller.balance < self.amount:
                raise ValidationError("Insufficient balance for this sale.")

            SellerProfile.objects.filter(id=self.seller.id).update(balance=F('balance') - self.amount)
            # self.seller.balance -= Decimal(self.amount)
            # self.seller.save()

        self.seller.refresh_from_db()
        # Log the sale in AccountEntry
        AccountEntry.objects.create(
            user=self.seller.user,
            entry_type=AccountEntry.SELL,
            amount=-self.amount,
            balance_after_entry=self.seller.balance
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

    seller = models.ForeignKey(SellerProfile, related_name="balance_increase_request", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)

    @db_transaction.atomic
    def approve(self):
        seller_lock_name = f"seller-{self.seller.id}-lock"  # Lock per seller

        # to prevent race conditions we use a thread-safe lock
        with acquire_thread_safe_lock(seller_lock_name):
            self.seller.refresh_from_db()

            if self.status == self.STATUS_ACCEPTED:
                # this guard prevents double-spending
                return

            self.status = self.STATUS_ACCEPTED
            self.save()
            self.__process_balance_increase()

        self.seller.refresh_from_db()
        # Log the recharge in AccountEntry
        AccountEntry.objects.create(
            user=self.seller.user,
            entry_type=AccountEntry.RECHARGE,
            amount=self.amount,
            balance_after_entry=self.seller.balance
        )

    @db_transaction.atomic
    def reject(self):
        self.status = self.STATUS_REJECTED
        self.save()

    def __process_balance_increase(self):
        if self.status == self.STATUS_ACCEPTED:
            SellerProfile.objects.filter(id=self.seller.id).update(balance=F('balance') + self.amount)
            # self.seller.balance += self.amount
            # self.seller.save()

    @db_transaction.atomic
    def save(self, *args, **kwargs):
        return super().save()

    def __str__(self):
        return f"Recharge for {self.seller.user.username} - ${self.amount} - {self.status.capitalize()}"
