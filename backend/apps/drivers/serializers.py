from rest_framework import serializers
from .models import Driver
from apps.accounts.serializers import UserSerializer


class DriverSerializer(serializers.ModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)

    class Meta:
        model = Driver
        fields = (
            'id', 'user', 'user_detail', 'driver_id', 'name', 'phone', 'address',
            'aadhaar', 'license_number', 'license_expiry', 'driver_photo',
            'bank_account', 'upi_id', 'status', 'joining_date'
        )
        read_only_fields = ('id', 'joining_date')
