from django.db import models
from apps.drivers.models import Driver
from apps.cars.models import Car


class Document(models.Model):
    class DocumentTypes(models.TextChoices):
        LICENSE = 'LICENSE', 'Driver License'
        AADHAAR = 'AADHAAR', 'Aadhaar Card'
        INSURANCE = 'INSURANCE', 'Vehicle Insurance'
        PERMIT = 'PERMIT', 'Vehicle Permit'
        FITNESS = 'FITNESS', 'Fitness Certificate'
        POLLUTION = 'POLLUTION', 'Pollution Certificate'
        OTHER = 'OTHER', 'Other Document'

    class Statuses(models.TextChoices):
        PENDING = 'PENDING', 'Pending Approval'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        EXPIRED = 'EXPIRED', 'Expired'

    driver = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents'
    )
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='documents'
    )
    document_type = models.CharField(max_length=30, choices=DocumentTypes.choices)
    document_number = models.CharField(max_length=50)
    expiry_date = models.DateField()
    document_file = models.FileField(upload_to='documents/')
    status = models.CharField(max_length=20, choices=Statuses.choices, default=Statuses.PENDING)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        owner = self.driver.name if self.driver else (self.car.registration_number if self.car else "System")
        return f"{self.get_document_type_display()} for {owner} ({self.get_status_display()})"
