from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from django.utils import timezone
from .models import Expense
from .serializers import ExpenseSerializer
from .tasks import process_cng_bill_ocr_task
from apps.accounts.permissions import IsManagerOrAbove


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all().order_by('-expense_date')
    serializer_class = ExpenseSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['driver', 'car', 'category', 'ocr_status', 'expense_date']
    search_fields = ['notes', 'vendor']

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'DRIVER':
            # Drivers can only see their own expense items
            return Expense.objects.filter(driver__user=user)
        return super().get_queryset()

    def perform_create(self, serializer):
        user = self.request.user
        
        # Determine driver and vehicle details if user is a driver
        if user.role == 'DRIVER':
            from apps.drivers.models import Driver
            try:
                driver = Driver.objects.get(user=user)
                # Auto-assign currently active vehicle
                assigned_car = driver.assigned_cars.first()
                
                # Check if this expense requires OCR
                receipt = self.request.FILES.get('receipt_photo')
                category = self.request.data.get('category', 'MISCELLANEOUS')
                
                ocr_status = Expense.OCRStatuses.NONE
                if receipt and category == 'FUEL':
                    ocr_status = Expense.OCRStatuses.PENDING

                expense = serializer.save(
                    driver=driver,
                    car=assigned_car,
                    ocr_status=ocr_status
                )
                
                # Launch task if OCR is required
                if ocr_status == Expense.OCRStatuses.PENDING:
                    process_cng_bill_ocr_task.delay(expense.id)
                    
            except Driver.DoesNotExist:
                raise Response({"error": "Driver profile not found."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Manager/admin creating expense
            receipt = self.request.FILES.get('receipt_photo')
            category = self.request.data.get('category')
            
            ocr_status = Expense.OCRStatuses.NONE
            if receipt and category == 'FUEL':
                ocr_status = Expense.OCRStatuses.PENDING
                
            expense = serializer.save(ocr_status=ocr_status)
            
            if ocr_status == Expense.OCRStatuses.PENDING:
                process_cng_bill_ocr_task.delay(expense.id)
                
    def update(self, request, *args, **kwargs):
        if request.user.role == 'DRIVER':
            return Response({"detail": "Drivers cannot modify expenses once uploaded."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
