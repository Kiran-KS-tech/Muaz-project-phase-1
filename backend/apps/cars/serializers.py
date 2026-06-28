from rest_framework import serializers
from .models import Car, ServiceRecord
from apps.drivers.serializers import DriverSerializer


class ServiceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRecord
        fields = ('id', 'car', 'service_date', 'description', 'cost', 'mileage_at_service', 'performed_by')


class CarSerializer(serializers.ModelSerializer):
    driver_detail = DriverSerializer(source='driver_assignment', read_only=True)
    service_records = ServiceRecordSerializer(many=True, read_only=True)

    class Meta:
        model = Car
        fields = (
            'id', 'registration_number', 'brand', 'model', 'year', 'fuel_type',
            'driver_assignment', 'driver_detail', 'insurance_number', 'insurance_expiry',
            'permit_number', 'permit_expiry', 'fitness_number', 'fitness_expiry',
            'pollution_certificate', 'pollution_expiry', 'status', 'service_records', 'created_at'
        )
        read_only_fields = ('id', 'created_at')
