from django.db import models
from django.conf import settings


class Notification(models.Model):
    class Types(models.TextChoices):
        INFO = 'INFO', 'Information'
        SETTLEMENT = 'SETTLEMENT', 'Settlement Update'
        ADVANCE = 'ADVANCE', 'Advance Request Update'
        DOCUMENT_EXPIRY = 'DOCUMENT_EXPIRY', 'Document Expiry Reminder'
        MAINTENANCE = 'MAINTENANCE', 'Scheduled Maintenance'

    class Severities(models.TextChoices):
        INFO = 'INFO', 'Low'
        WARNING = 'WARNING', 'Medium'
        CRITICAL = 'CRITICAL', 'High'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    title = models.CharField(max_length=150)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=Types.choices, default=Types.INFO)
    severity = models.CharField(max_length=20, choices=Severities.choices, default=Severities.INFO)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.get_severity_display()}"
