from celery import shared_task
from django.utils import timezone
from .models import Car
from apps.notifications.models import Notification


@shared_task
def check_upcoming_maintenance():
    """
    Scans all active vehicles and flags those that haven't been serviced in the last 180 days.
    """
    threshold_date = timezone.now().date() - timezone.timedelta(days=180)
    # Cars that have service records older than threshold, or no service records at all
    cars_to_alert = Car.objects.filter(status=Car.Statuses.ACTIVE)
    
    alert_count = 0
    for car in cars_to_alert:
        last_service = car.service_records.order_by('-service_date').first()
        if not last_service or last_service.service_date <= threshold_date:
            # Create a notification for managers/owners
            Notification.objects.create(
                title=f"Maintenance Alert: {car.registration_number}",
                message=f"Vehicle {car.brand} {car.model} ({car.registration_number}) is due for scheduled maintenance. Last service date: {last_service.service_date if last_service else 'Never'}.",
                notification_type=Notification.Types.MAINTENANCE,
                severity=Notification.Severities.WARNING
            )
            alert_count += 1
            
    return f"Maintenance check completed. Generated {alert_count} alerts."
