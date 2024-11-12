from rest_framework import serializers
from .models import StatusModel

class StatusModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusModel
        fields = ['id', 'name', 'status']
