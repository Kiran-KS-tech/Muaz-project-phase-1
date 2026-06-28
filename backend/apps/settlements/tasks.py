from celery import shared_task
from django.utils import timezone
from django.db.models import Sum
from django.conf import settings
from datetime import timedelta
from .models import Settlement
from apps.drivers.models import Driver
from apps.earnings.models import EarningUpload
from apps.expenses.models import Expense
from apps.advances.models import AdvanceRequest
from apps.notifications.models import Notification


@shared_task
def generate_weekly_settlements():
    """
    Periodic task running weekly (Sunday midnight) to generate settlements for the past week.
    Calculates: Monday to Sunday of the week just ended.
    """
    today = timezone.now().date()
    # Find start and end date of last week
    end_date = today - timedelta(days=1)  # Sunday
    start_date = end_date - timedelta(days=6)  # Monday

    return generate_settlements_for_range(start_date, end_date)


def generate_settlements_for_range(start_date, end_date):
    """
    Generates settlements for all active drivers for a specific date range.
    """
    drivers = Driver.objects.filter(status=Driver.Statuses.ACTIVE)
    commission_pct = getattr(settings, 'COMPANY_COMMISSION_PERCENTAGE', 15.0)
    created_count = 0

    for driver in drivers:
        # Check if settlement already exists for this driver and range
        if Settlement.objects.filter(driver=driver, start_date=start_date, end_date=end_date).exists():
            continue

        # 1. Sum up Gross Earnings and Cash Collected
        earnings_qs = EarningUpload.objects.filter(
            driver=driver,
            earnings_date__range=[start_date, end_date],
            ocr_status=EarningUpload.OCRStatuses.SUCCESS
        )
        gross = earnings_qs.aggregate(total=Sum('gross_earnings'))['total'] or 0.00
        cash = earnings_qs.aggregate(total=Sum('cash_collected'))['total'] or 0.00

        # 2. Sum up Approved Expenses
        expenses_amount = Expense.objects.filter(
            driver=driver,
            expense_date__range=[start_date, end_date]
        ).aggregate(total=Sum('amount'))['total'] or 0.00

        # 3. Sum up Approved Advances
        advances_amount = AdvanceRequest.objects.filter(
            driver=driver,
            request_date__range=[start_date, end_date],
            status=AdvanceRequest.Statuses.APPROVED
        ).aggregate(total=Sum('amount'))['total'] or 0.00

        # 4. Calculate Fleet Commission
        commission = round((gross * commission_pct) / 100, 2)

        # 5. Create Settlement
        settlement = Settlement(
            driver=driver,
            start_date=start_date,
            end_date=end_date,
            gross_earnings=gross,
            cash_collected=cash,
            expenses_amount=expenses_amount,
            advances_amount=advances_amount,
            commission_amount=commission,
            status=Settlement.Statuses.PENDING
        )
        settlement.save()
        created_count += 1

        # Notify driver
        if driver.user:
            Notification.objects.create(
                user=driver.user,
                title="Weekly Settlement Generated",
                message=f"Your settlement for the period {start_date} to {end_date} has been generated. Net Payout: ₹{settlement.final_settlement_amount}. Pending approval.",
                notification_type=Notification.Types.SETTLEMENT,
                severity=Notification.Severities.INFO
            )

    return f"Generated {created_count} settlements for range {start_date} to {end_date}."
