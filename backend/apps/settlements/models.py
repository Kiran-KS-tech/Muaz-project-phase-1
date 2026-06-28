from django.db import models
from apps.drivers.models import Driver


class Settlement(models.Model):
    class Statuses(models.TextChoices):
        PENDING = 'PENDING', 'Pending Approval'
        APPROVED = 'APPROVED', 'Approved'
        PAID = 'PAID', 'Paid'

    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='settlements')
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Financial breakdown
    gross_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    cash_collected = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    expenses_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    advances_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    manual_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    manual_adjustment_reason = models.TextField(blank=True, null=True)
    final_settlement_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    status = models.CharField(max_length=20, choices=Statuses.choices, default=Statuses.PENDING)
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_totals(self):
        self.net_amount = (
            self.gross_earnings - 
            self.cash_collected - 
            self.expenses_amount - 
            self.advances_amount - 
            self.commission_amount
        )
        self.final_settlement_amount = self.net_amount + self.manual_adjustment

    def save(self, *args, **kwargs):
        self.calculate_totals()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Settlement for {self.driver.name} (₹{self.final_settlement_amount}) [{self.start_date} to {self.end_date}]"
