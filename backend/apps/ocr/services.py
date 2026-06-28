import os
import random
from datetime import date
from django.conf import settings


class OCRProcessor:
    def __init__(self):
        self.provider = getattr(settings, 'OCR_PROVIDER', 'mock').lower()

    def process_uber_screenshot(self, image_file):
        """
        Parses Uber driver weekly/daily summary.
        Extracts: gross_earnings, cash_collected, incentives, trips, earnings_date
        """
        if self.provider == 'mock':
            return self._mock_uber_parsing(image_file)
        elif self.provider == 'google':
            return self._google_vision_ocr(image_file, "uber")
        elif self.provider == 'aws':
            return self._aws_textract_ocr(image_file, "uber")
        
        return self._mock_uber_parsing(image_file)

    def process_driving_license(self, image_file):
        """
        Parses Driving License card photos.
        Extracts: name, license_number, license_expiry
        """
        if self.provider == 'mock':
            return self._mock_license_parsing(image_file)
        elif self.provider == 'google':
            return self._google_vision_ocr(image_file, "license")
        elif self.provider == 'aws':
            return self._aws_textract_ocr(image_file, "license")

        return self._mock_license_parsing(image_file)


    def process_cng_bill(self, image_file):
        """
        Parses CNG fuel receipts.
        Extracts: date, amount, vendor, quantity
        """
        if self.provider == 'mock':
            return self._mock_cng_parsing(image_file)
        elif self.provider == 'google':
            return self._google_vision_ocr(image_file, "cng")
        elif self.provider == 'aws':
            return self._aws_textract_ocr(image_file, "cng")

        return self._mock_cng_parsing(image_file)

    def _mock_uber_parsing(self, image_file):
        # Return sensible data for demonstration / mock runs
        # Try to vary output slightly for testing
        file_name = image_file.name.lower() if hasattr(image_file, 'name') else ""
        
        # Determine gross from filename if possible for deterministic testing
        gross = 8500.00
        cash = 1200.00
        incentives = 800.00
        trips = 32

        if "high" in file_name:
            gross = 15000.00
            cash = 2500.00
            incentives = 2000.00
            trips = 55
        elif "low" in file_name:
            gross = 4200.00
            cash = 500.00
            incentives = 300.00
            trips = 15
        else:
            # Randomize slightly to make it feel dynamic
            gross = round(random.uniform(5000, 12000), 2)
            cash = round(random.uniform(500, 2000), 2)
            incentives = round(random.uniform(300, 1500), 2)
            trips = random.randint(20, 45)

        return {
            "gross_earnings": gross,
            "cash_collected": cash,
            "incentives": incentives,
            "trips": trips,
            "earnings_date": str(date.today()),
            "status": "success",
            "provider": "mock-ocr"
        }

    def _mock_cng_parsing(self, image_file):
        file_name = image_file.name.lower() if hasattr(image_file, 'name') else ""
        
        amount = 450.00
        qty = 6.5

        if "expensive" in file_name:
            amount = 950.00
            qty = 13.8
        else:
            amount = round(random.uniform(300, 750), 2)
            qty = round(amount / 68.5, 2)  # Assuming CNG rate is ~68.5 per kg

        stations = ["Indraprastha Gas CNG Station", "Mahanagar Gas Fuel Point", "Adani Gas CNG Stn"]
        
        return {
            "amount": amount,
            "date": str(date.today()),
            "vendor": random.choice(stations),
            "quantity": qty,
            "status": "success",
            "provider": "mock-ocr"
        }

    def _mock_license_parsing(self, image_file):
        file_name = image_file.name.lower() if hasattr(image_file, 'name') else ""
        
        # Default mock output
        name = "Aman Verma"
        lic_no = "DL-1420250089765"
        expiry = "2035-08-20"

        if "priya" in file_name:
            name = "Priya Sharma"
            lic_no = "MH-1220230009854"
            expiry = "2038-04-12"
        elif "john" in file_name:
            name = "John Doe"
            lic_no = "HR-2620210088776"
            expiry = "2031-11-05"

        return {
            "name": name,
            "license_number": lic_no,
            "license_expiry": expiry,
            "status": "success",
            "provider": "mock-ocr"
        }

    def _google_vision_ocr(self, image_file, document_type):
        """
        Skeleton for Google Vision API.
        Requires google-cloud-vision to be installed.
        """
        print(f"[GOOGLE VISION OCR] Simulating API call for {document_type}...")
        if document_type == "uber":
            return self._mock_uber_parsing(image_file)
        elif document_type == "license":
            return self._mock_license_parsing(image_file)
        return self._mock_cng_parsing(image_file)

    def _aws_textract_ocr(self, image_file, document_type):
        """
        Skeleton for AWS Textract API.
        Requires boto3.
        """
        print(f"[AWS TEXTRACT OCR] Simulating API call for {document_type}...")
        if document_type == "uber":
            return self._mock_uber_parsing(image_file)
        elif document_type == "license":
            return self._mock_license_parsing(image_file)
        return self._mock_cng_parsing(image_file)

