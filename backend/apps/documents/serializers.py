from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source='driver.name', read_only=True)
    car_reg = serializers.CharField(source='car.registration_number', read_only=True)

    class Meta:
        model = Document
        fields = (
            'id', 'driver', 'driver_name', 'car', 'car_reg', 'document_type',
            'document_number', 'expiry_date', 'document_file', 'status', 'uploaded_at'
        )
        read_only_fields = ('id', 'uploaded_at')
