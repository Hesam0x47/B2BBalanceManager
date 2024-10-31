from rest_framework import serializers

from .models import AccountEntry


class AccountEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountEntry
        fields = ['id', 'user', 'entry_type', 'amount', 'balance_after_entry', 'timestamp']
        read_only_fields = fields
