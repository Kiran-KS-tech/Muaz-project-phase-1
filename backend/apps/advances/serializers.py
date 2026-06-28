from rest_framework import serializers
from .models import AdvanceRequest


class AdvanceRequestSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source='driver.name', read_only=True)

    class Meta:
        model = AdvanceRequest
        fields = (
            'id', 'driver', 'driver_name', 'amount', 'reason',
            'status', 'admin_notes', 'request_date', 'resolved_date'
        )
        read_only_fields = ('id', 'status', 'request_date', 'resolved_date')
