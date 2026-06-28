from django.db import models
from apps.drivers.models import Driver


class EarningUpload(models.Model):
    class OCRStatuses(models.TextChoices):
        PENDING = 'PENDING', 'Pending Processing'
        PROCESSING = 'PROCESSING', 'Processing OCR'
        SUCCESS = 'SUCCESS', 'Success'
        FAILED = 'FAILED', 'Failed'

    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='earnings_uploads')
    screenshot = models.ImageField(upload_to='earnings/screenshots/')
    
    # OCR Extracted and Admin Audited data
    gross_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    cash_collected = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    incentives = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    trips = models.PositiveIntegerField(default=0)
    earnings_date = models.DateField(null=True, blank=True)
    
    ocr_status = models.CharField(max_length=20, choices=OCRStatuses.choices, default=OCRStatuses.PENDING)
    ocr_raw_result = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Earnings upload for {self.driver.name} on {self.created_at.date()} ({self.get_ocr_status_display()})"
