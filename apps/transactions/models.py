from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import F

from helpers.lock import acquire_thread_safe_lock


class Seller(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, null=False, blank=False)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.name} - Balance: {self.balance}"


class Transaction(models.Model):
    SELL = 'sell'
    RECHARGE = 'recharge'
    TRANSACTION_TYPES = [
        (SELL, 'Sell'),
        (RECHARGE, 'Recharge'),
    ]

    seller = models.ForeignKey(Seller, related_name="transactions", on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    @transaction.atomic
    def save(self, *args, **kwargs):
        """
        Saves the transaction object to the database

        Use atomic transaction to prevent double spending
        :param args:
        :param kwargs:
        :return:
        """
        with acquire_thread_safe_lock(f'seller-{self.seller.id}-lock'):
            # Lock the seller row to prevent concurrent updates
            seller = Seller.objects.select_for_update().get(id=self.seller.id)

            if self.transaction_type == self.SELL:
                # Ensure there's enough balance to perform the transaction
                if seller.balance < self.amount:
                    raise ValidationError("Insufficient balance for this transaction.")
                seller.balance = F('balance') - self.amount
            elif self.transaction_type == self.RECHARGE:
                seller.balance = F('balance') + self.amount

            # Save the balance update
            seller.save()
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.seller.name} - {self.transaction_type.capitalize()} - ${self.amount}"


class Recharge(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    seller = models.ForeignKey(Seller, related_name="recharges", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_successful = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)

    def process_recharge(self, **kwargs):
        """Update balance only if status is 'accepted' and the recharge is not already processed."""
        new_status = kwargs.get('action')
        if self.status != self.STATUS_PENDING:
            return

        if new_status == self.STATUS_ACCEPTED:
            self.seller.balance += self.amount
            self.seller.save()

        self.status = new_status
        self.save()

    def __str__(self):
        return f"Recharge for {self.seller.name} - ${self.amount} - {self.status.capitalize()}"
