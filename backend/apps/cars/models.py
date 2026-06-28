from django.db import models
from apps.drivers.models import Driver


class Car(models.Model):
    class FuelTypes(models.TextChoices):
        CNG = 'CNG', 'CNG'
        PETROL = 'PETROL', 'Petrol'
        DIESEL = 'DIESEL', 'Diesel'
        ELECTRIC = 'ELECTRIC', 'Electric'

    class Statuses(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        MAINTENANCE = 'MAINTENANCE', 'In Maintenance'
        OUT_OF_SERVICE = 'OUT_OF_SERVICE', 'Out of Service'

    registration_number = models.CharField(max_length=20, unique=True)
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    fuel_type = models.CharField(max_length=15, choices=FuelTypes.choices, default=FuelTypes.CNG)
    driver_assignment = models.ForeignKey(
        Driver,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_cars'
    )
    
    # Expiry Documents info
    insurance_number = models.CharField(max_length=50, blank=True, null=True)
    insurance_expiry = models.DateField(blank=True, null=True)
    
    permit_number = models.CharField(max_length=50, blank=True, null=True)
    permit_expiry = models.DateField(blank=True, null=True)
    
    fitness_number = models.CharField(max_length=50, blank=True, null=True)
    fitness_expiry = models.DateField(blank=True, null=True)
    
    pollution_certificate = models.CharField(max_length=50, blank=True, null=True)
    pollution_expiry = models.DateField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=Statuses.choices, default=Statuses.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand} {self.model} ({self.registration_number})"


class ServiceRecord(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='service_records')
    service_date = models.DateField()
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    mileage_at_service = models.PositiveIntegerField(blank=True, null=True)
    performed_by = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Service for {self.car.registration_number} on {self.service_date}"
