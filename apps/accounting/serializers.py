from rest_framework import serializers

from .models import AccountingEntry


class AccountingEntrySerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = AccountingEntry
        fields = ['id', 'user', 'entry_type', 'amount', 'balance_after_entry', 'timestamp']
        read_only_fields = fields
