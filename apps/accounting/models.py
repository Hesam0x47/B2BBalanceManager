from django.conf import settings
from django.db import models


class AccountingEntry(models.Model):
    RECHARGE = 'recharge'
    SELL = 'sell'
    ENTRY_TYPE_CHOICES = [
        (RECHARGE, 'Recharge'),  # When seller adds funds
        (SELL, 'Sell'),  # When seller sells to a customer
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    entry_type = models.CharField(max_length=10, choices=ENTRY_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after_entry = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.entry_type} - {self.amount} at {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']
