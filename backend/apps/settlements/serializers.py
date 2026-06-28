from rest_framework import serializers
from .models import Settlement


class SettlementSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source='driver.name', read_only=True)
    bank_account = serializers.CharField(source='driver.bank_account', read_only=True)
    upi_id = serializers.CharField(source='driver.upi_id', read_only=True)

    class Meta:
        model = Settlement
        fields = (
            'id', 'driver', 'driver_name', 'bank_account', 'upi_id',
            'start_date', 'end_date', 'gross_earnings', 'cash_collected',
            'expenses_amount', 'advances_amount', 'commission_amount',
            'net_amount', 'manual_adjustment', 'manual_adjustment_reason',
            'final_settlement_amount', 'status', 'payment_reference', 'paid_at', 'created_at'
        )
        read_only_fields = ('id', 'net_amount', 'final_settlement_amount', 'created_at')
