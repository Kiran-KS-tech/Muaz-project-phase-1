import json
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from django.contrib.auth.signals import user_logged_in, user_logged_out
from .models import AuditLog
from .middleware import get_current_user, get_current_ip

# Models to track
from apps.drivers.models import Driver
from apps.cars.models import Car
from apps.earnings.models import EarningUpload
from apps.expenses.models import Expense
from apps.advances.models import AdvanceRequest
from apps.settlements.models import Settlement

TRACKED_MODELS = (Driver, Car, EarningUpload, Expense, AdvanceRequest, Settlement)


def serialize_model(instance):
    """
    Safely serializes a model instance into a JSON-serializable dictionary.
    """
    try:
        # Convert to dictionary representation
        data = model_to_dict(instance)
        # Resolve files and complex objects to string path / IDs
        for k, v in list(data.items()):
            if hasattr(v, 'url'):  # Image / File Fields
                data[k] = v.url
        return json.loads(json.dumps(data, cls=DjangoJSONEncoder))
    except Exception as e:
        return {"id": getattr(instance, 'id', None), "error": str(e)}


@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    if sender not in TRACKED_MODELS:
        return

    # Fetch request context details
    user = get_current_user()
    ip = get_current_ip()
    action = "CREATE" if created else "UPDATE"
    new_val = serialize_model(instance)

    # For specialized actions, customize the action string
    if sender == Settlement and not created:
        if new_val.get('status') == 'APPROVED':
            action = "SETTLEMENT_APPROVAL"
        elif new_val.get('status') == 'PAID':
            action = "SETTLEMENT_PAYOUT"
    elif sender == EarningUpload and not created:
        if new_val.get('ocr_status') == 'SUCCESS':
            action = "OCR_COMPLETE"

    AuditLog.objects.create(
        user=user,
        action=action,
        model_name=sender.__name__,
        object_id=str(instance.id),
        previous_value=None,
        new_value=new_val,
        ip_address=ip
    )


@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):
    if sender not in TRACKED_MODELS:
        return

    user = get_current_user()
    ip = get_current_ip()

    AuditLog.objects.create(
        user=user,
        action="DELETE",
        model_name=sender.__name__,
        object_id=str(instance.id),
        previous_value=serialize_model(instance),
        new_value=None,
        ip_address=ip
    )


@receiver(user_logged_in)
def audit_login(sender, request, user, **kwargs):
    # Fetch client IP from request if available
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.META.get('REMOTE_ADDR')

    AuditLog.objects.create(
        user=user,
        action="LOGIN",
        model_name="User",
        object_id=str(user.id),
        ip_address=ip
    )
