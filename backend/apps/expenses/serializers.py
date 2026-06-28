from rest_framework import serializers
from .models import Expense


class ExpenseSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source='driver.name', read_only=True)
    car_reg = serializers.CharField(source='car.registration_number', read_only=True)

    class Meta:
        model = Expense
        fields = (
            'id', 'driver', 'driver_name', 'car', 'car_reg', 'category',
            'amount', 'expense_date', 'receipt_photo', 'notes',
            'quantity', 'vendor', 'ocr_status', 'ocr_raw_result', 'created_at'
        )
        read_only_fields = ('id', 'ocr_status', 'ocr_raw_result', 'created_at')
