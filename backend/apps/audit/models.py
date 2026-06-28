from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=50)  # CREATE, UPDATE, DELETE, LOGIN, SETTLEMENT_APPROVAL, OCR_EDIT
    model_name = models.CharField(max_length=100, blank=True, null=True)
    object_id = models.CharField(max_length=50, blank=True, null=True)
    previous_value = models.JSONField(blank=True, null=True)
    new_value = models.JSONField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        actor = self.user.email if self.user else "System"
        return f"{self.action} on {self.model_name or 'Auth'} by {actor} at {self.timestamp}"
