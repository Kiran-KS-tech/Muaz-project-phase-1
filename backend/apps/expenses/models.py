from django.db import models
from apps.drivers.models import Driver
from apps.cars.models import Car


class Expense(models.Model):
    class Categories(models.TextChoices):
        FUEL = 'FUEL', 'Fuel / CNG'
        REPAIR = 'REPAIR', 'Repair & Maintenance'
        CAR_WASH = 'CAR_WASH', 'Car Wash'
        PARKING = 'PARKING', 'Parking'
        TYRE = 'TYRE', 'Tyre Service'
        MISCELLANEOUS = 'MISCELLANEOUS', 'Miscellaneous'

    class OCRStatuses(models.TextChoices):
        NONE = 'NONE', 'No OCR Required'
        PENDING = 'PENDING', 'Pending OCR'
        PROCESSING = 'PROCESSING', 'Processing OCR'
        SUCCESS = 'SUCCESS', 'Success'
        FAILED = 'FAILED', 'Failed'

    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='expenses')
    car = models.ForeignKey(Car, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses')
    category = models.CharField(max_length=30, choices=Categories.choices, default=Categories.MISCELLANEOUS)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    expense_date = models.DateField()
    receipt_photo = models.ImageField(upload_to='expenses/receipts/', blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # CNG receipt OCR details
    quantity = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)  # in kg/liters
    vendor = models.CharField(max_length=150, blank=True, null=True)
    ocr_status = models.CharField(max_length=20, choices=OCRStatuses.choices, default=OCRStatuses.NONE)
    ocr_raw_result = models.JSONField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_category_display()} - ₹{self.amount} by {self.driver.name} on {self.expense_date}"
