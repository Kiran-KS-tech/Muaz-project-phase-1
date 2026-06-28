from django.db import models
from django.conf import settings


class Driver(models.Model):
    class Statuses(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        SUSPENDED = 'SUSPENDED', 'Suspended'
        PENDING = 'PENDING', 'Pending'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='driver_profile'
    )
    driver_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    address = models.TextField(blank=True, null=True)
    aadhaar = models.CharField(max_length=20, unique=True, blank=True, null=True)
    license_number = models.CharField(max_length=50, unique=True)
    license_expiry = models.DateField()
    driver_photo = models.ImageField(upload_to='drivers/photos/', blank=True, null=True)
    bank_account = models.CharField(max_length=50, blank=True, null=True)
    upi_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=Statuses.choices, default=Statuses.PENDING)
    joining_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.driver_id})"
