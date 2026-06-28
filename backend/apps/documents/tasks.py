from celery import shared_task
from django.utils import timezone
from .models import Document
from apps.notifications.models import Notification
from apps.notifications.tasks import send_whatsapp_notification


@shared_task
def check_document_expiries():
    """
    Periodic task running daily at midnight to scan document expiries.
    Triggers warnings at 30 days, 7 days, 1 day, and updates state to EXPIRED on deadline.
    """
    today = timezone.now().date()
    
    # 1. Update documents that have passed their expiry date
    expired_docs = Document.objects.filter(expiry_date__lte=today, status=Document.Statuses.APPROVED)
    expired_count = expired_docs.count()
    for doc in expired_docs:
        doc.status = Document.Statuses.EXPIRED
        doc.save(update_fields=['status'])
        
        # Create critical alert
        recipient = doc.driver.user if doc.driver else None
        Notification.objects.create(
            user=recipient,
            title=f"DOCUMENT EXPIRED: {doc.get_document_type_display()}",
            message=f"The {doc.get_document_type_display()} has expired on {doc.expiry_date}. Please upload a renewed document immediately.",
            notification_type=Notification.Types.DOCUMENT_EXPIRY,
            severity=Notification.Severities.CRITICAL
        )
        
        # Dispatch simulated SMS / WhatsApp alert
        if doc.driver and doc.driver.phone:
            send_whatsapp_notification.delay(
                phone_number=doc.driver.phone,
                template_name="doc_expired_alert",
                parameters={"doc_name": doc.get_document_type_display(), "expiry_date": str(doc.expiry_date)}
            )

    # 2. Check for upcoming expiries in 30 days, 7 days, and 1 day
    for days_ahead in [30, 7, 1]:
        alert_date = today + timezone.timedelta(days=days_ahead)
        expiring_soon = Document.objects.filter(expiry_date=alert_date, status=Document.Statuses.APPROVED)
        
        for doc in expiring_soon:
            recipient = doc.driver.user if doc.driver else None
            severity = Notification.Severities.WARNING if days_ahead <= 7 else Notification.Severities.INFO
            
            Notification.objects.create(
                user=recipient,
                title=f"Document Expiring in {days_ahead} Days",
                message=f"The {doc.get_document_type_display()} is set to expire on {doc.expiry_date}.",
                notification_type=Notification.Types.DOCUMENT_EXPIRY,
                severity=severity
            )
            
            if doc.driver and doc.driver.phone:
                send_whatsapp_notification.delay(
                    phone_number=doc.driver.phone,
                    template_name="doc_expiry_warning",
                    parameters={"doc_name": doc.get_document_type_display(), "days": days_ahead, "expiry_date": str(doc.expiry_date)}
                )

    return f"Expiry scan completed. Marked {expired_count} documents as EXPIRED."
