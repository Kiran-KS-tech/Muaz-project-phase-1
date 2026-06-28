from django.db import models
from apps.drivers.models import Driver


class AdvanceRequest(models.Model):
    class Statuses(models.TextChoices):
        PENDING = 'PENDING', 'Pending Approval'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='advance_requests')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=Statuses.choices, default=Statuses.PENDING)
    admin_notes = models.TextField(blank=True, null=True)
    request_date = models.DateField(auto_now_add=True)
    resolved_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Advance request of ₹{self.amount} by {self.driver.name} ({self.get_status_display()})"
