from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CreditIncreaseRequestModel
from ..accounting.models import AccountEntry


@receiver(post_save, sender=CreditIncreaseRequestModel)
def create_account_entry_for_recharge(sender, instance, created, **kwargs):
    if created:
        # # Update seller's balance
        # instance.seller.balance += instance.amount
        # instance.seller.save()

        # Log the recharge action
        AccountEntry.objects.create(
            user=instance.seller.user,
            entry_type=AccountEntry.RECHARGE,
            amount=instance.amount,
            balance_after_entry=instance.seller.balance
        )
