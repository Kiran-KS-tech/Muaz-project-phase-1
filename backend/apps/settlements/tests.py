from django.test import TestCase
from django.utils import timezone
from datetime import date
from apps.accounts.models import User
from apps.drivers.models import Driver
from apps.earnings.models import EarningUpload
from apps.expenses.models import Expense
from apps.advances.models import AdvanceRequest
from apps.settlements.models import Settlement
from apps.settlements.tasks import generate_settlements_for_range


class SettlementCalculationTestCase(TestCase):
    def setUp(self):
        # 1. Create a user and driver profile
        self.user = User.objects.create_user(
            email="driver_test@company.com",
            password="testpassword123",
            phone_number="+919998887776",
            role=User.Roles.DRIVER
        )
        self.driver = Driver.objects.create(
            user=self.user,
            driver_id="DRV-TEST-01",
            name="Test Driver",
            phone="+919998887776",
            license_number="DL-TEST-992211",
            license_expiry=date(2030, 1, 1),
            status=Driver.Statuses.ACTIVE
        )

        # Date range for settlements (e.g. this week)
        self.start_date = date(2026, 6, 1)
        self.end_date = date(2026, 6, 7)

    def test_settlement_math_formula(self):
        """
        Validates the payout calculation formula:
        Settlement = Gross - Cash Collected - Expenses - Advances - Commission (15%)
        """
        # 1. Create mock earnings (Gross: 10000, Cash Collected: 2000)
        EarningUpload.objects.create(
            driver=self.driver,
            gross_earnings=10000.00,
            cash_collected=2000.00,
            incentives=1000.00,
            trips=25,
            earnings_date=date(2026, 6, 3),
            ocr_status=EarningUpload.OCRStatuses.SUCCESS
        )

        # 2. Create mock expenses (Total: 850)
        Expense.objects.create(
            driver=self.driver,
            category=Expense.Categories.FUEL,
            amount=850.00,
            expense_date=date(2026, 6, 4)
        )

        # 3. Create mock advances (Total: 1500)
        AdvanceRequest.objects.create(
            driver=self.driver,
            amount=1500.00,
            reason="Tire repair advance",
            status=AdvanceRequest.Statuses.APPROVED,
            request_date=date(2026, 6, 5)
        )

        # 4. Calculate expected settlement
        # Gross = 10000.00
        # Cash Collected = 2000.00
        # Expenses = 850.00
        # Advances = 1500.00
        # Commission (15% of 10000) = 1500.00
        # Expected Net = 10000.00 - 2000.00 - 850.00 - 1500.00 - 1500.00 = 4150.00
        
        generate_settlements_for_range(self.start_date, self.end_date)

        # Verify settlement creation
        settlements = Settlement.objects.filter(driver=self.driver, start_date=self.start_date, end_date=self.end_date)
        self.assertEqual(settlements.count(), 1)
        
        settlement = settlements.first()
        self.assertEqual(float(settlement.gross_earnings), 10000.00)
        self.assertEqual(float(settlement.cash_collected), 2000.00)
        self.assertEqual(float(settlement.expenses_amount), 850.00)
        self.assertEqual(float(settlement.advances_amount), 1500.00)
        self.assertEqual(float(settlement.commission_amount), 1500.00)
        self.assertEqual(float(settlement.final_settlement_amount), 4150.00)
