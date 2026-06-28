from celery import shared_task
from django.db import transaction
from .models import EarningUpload
from apps.ocr.services import OCRProcessor
from apps.notifications.models import Notification


@shared_task
def process_earning_ocr_task(upload_id):
    """
    Celery task that reads the screenshot, runs OCR text extraction,
    and updates the EarningUpload record.
    """
    try:
        upload = EarningUpload.objects.get(id=upload_id)
    except EarningUpload.DoesNotExist:
        return f"Upload {upload_id} not found."

    # Mark status as PROCESSING
    upload.ocr_status = EarningUpload.OCRStatuses.PROCESSING
    upload.save(update_fields=['ocr_status'])

    try:
        processor = OCRProcessor()
        # Open screenshot and run OCR
        result = processor.process_uber_screenshot(upload.screenshot)
        
        with transaction.atomic():
            if result.get("status") == "success":
                upload.gross_earnings = result.get("gross_earnings", 0.00)
                upload.cash_collected = result.get("cash_collected", 0.00)
                upload.incentives = result.get("incentives", 0.00)
                upload.trips = result.get("trips", 0)
                upload.earnings_date = result.get("earnings_date")
                upload.ocr_status = EarningUpload.OCRStatuses.SUCCESS
                upload.ocr_raw_result = result
                upload.save()
                
                # Send push / system notification to the driver
                if upload.driver.user:
                    Notification.objects.create(
                        user=upload.driver.user,
                        title="Uber Screenshot Processed",
                        message=f"Your uploaded screenshot from {upload.earnings_date or 'today'} has been processed. Gross Earnings: ₹{upload.gross_earnings}, Cash Collected: ₹{upload.cash_collected}.",
                        notification_type=Notification.Types.SETTLEMENT,
                        severity=Notification.Severities.INFO
                    )
            else:
                upload.ocr_status = EarningUpload.OCRStatuses.FAILED
                upload.ocr_raw_result = result
                upload.save()
                
                if upload.driver.user:
                    Notification.objects.create(
                        user=upload.driver.user,
                        title="Uber Screenshot Processing Failed",
                        message="We were unable to parse your uploaded Uber screenshot. An administrator has been notified to review it manually.",
                        notification_type=Notification.Types.SETTLEMENT,
                        severity=Notification.Severities.WARNING
                    )
    except Exception as e:
        upload.ocr_status = EarningUpload.OCRStatuses.FAILED
        upload.ocr_raw_result = {"error": str(e)}
        upload.save()
        
        if upload.driver.user:
            Notification.objects.create(
                user=upload.driver.user,
                title="Uber Screenshot Processing Error",
                message="A system error occurred while processing your screenshot. It will be reviewed manually.",
                notification_type=Notification.Types.SETTLEMENT,
                severity=Notification.Severities.CRITICAL
            )
        return f"Error processing OCR: {str(e)}"
        
    return f"Successfully processed OCR for EarningUpload ID {upload_id}"
