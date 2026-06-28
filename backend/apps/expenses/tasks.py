from celery import shared_task
from django.db import transaction
from .models import Expense
from apps.ocr.services import OCRProcessor
from apps.notifications.models import Notification


@shared_task
def process_cng_bill_ocr_task(expense_id):
    """
    Celery task to run OCR on CNG receipts and populate Expense details.
    """
    try:
        expense = Expense.objects.get(id=expense_id)
    except Expense.DoesNotExist:
        return f"Expense {expense_id} not found."

    expense.ocr_status = Expense.OCRStatuses.PROCESSING
    expense.save(update_fields=['ocr_status'])

    try:
        processor = OCRProcessor()
        result = processor.process_cng_bill(expense.receipt_photo)

        with transaction.atomic():
            if result.get("status") == "success":
                expense.amount = result.get("amount", expense.amount)
                expense.expense_date = result.get("date", expense.expense_date)
                expense.vendor = result.get("vendor", expense.vendor)
                expense.quantity = result.get("quantity", expense.quantity)
                expense.ocr_status = Expense.OCRStatuses.SUCCESS
                expense.ocr_raw_result = result
                expense.save()

                if expense.driver.user:
                    Notification.objects.create(
                        user=expense.driver.user,
                        title="CNG Bill Processed",
                        message=f"Your uploaded CNG receipt has been parsed. Vendor: {expense.vendor}, Amount: ₹{expense.amount}, Qty: {expense.quantity} kg.",
                        notification_type=Notification.Types.INFO,
                        severity=Notification.Severities.INFO
                    )
            else:
                expense.ocr_status = Expense.OCRStatuses.FAILED
                expense.ocr_raw_result = result
                expense.save()

                if expense.driver.user:
                    Notification.objects.create(
                        user=expense.driver.user,
                        title="CNG Receipt parsing failed",
                        message="We were unable to parse your CNG receipt automatically. It will be reviewed manually.",
                        notification_type=Notification.Types.INFO,
                        severity=Notification.Severities.WARNING
                    )
    except Exception as e:
        expense.ocr_status = Expense.OCRStatuses.FAILED
        expense.ocr_raw_result = {"error": str(e)}
        expense.save()

        if expense.driver.user:
            Notification.objects.create(
                user=expense.driver.user,
                title="CNG Receipt processing error",
                message=f"An error occurred while running OCR on your CNG bill: {str(e)}",
                notification_type=Notification.Types.INFO,
                severity=Notification.Severities.CRITICAL
            )
        return f"Error running CNG OCR: {str(e)}"

    return f"CNG OCR task finished for Expense ID {expense_id}"
