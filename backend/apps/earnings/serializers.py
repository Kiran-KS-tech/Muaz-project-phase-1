from rest_framework import serializers
from .models import EarningUpload


class EarningUploadSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source='driver.name', read_only=True)

    class Meta:
        model = EarningUpload
        fields = (
            'id', 'driver', 'driver_name', 'screenshot', 'gross_earnings',
            'cash_collected', 'incentives', 'trips', 'earnings_date',
            'ocr_status', 'ocr_raw_result', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'ocr_status', 'ocr_raw_result', 'created_at', 'updated_at')
