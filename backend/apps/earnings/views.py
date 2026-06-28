from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import EarningUpload
from .serializers import EarningUploadSerializer
from .tasks import process_earning_ocr_task
from apps.accounts.permissions import IsManagerOrAbove, IsDriver


class EarningUploadViewSet(viewsets.ModelViewSet):
    queryset = EarningUpload.objects.all().order_by('-created_at')
    serializer_class = EarningUploadSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['driver', 'ocr_status', 'earnings_date']

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'DRIVER':
            # Drivers can only see their own screenshot uploads
            return EarningUpload.objects.filter(driver__user=user)
        return super().get_queryset()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'DRIVER':
            from apps.drivers.models import Driver
            try:
                driver = Driver.objects.get(user=user)
                upload = serializer.save(driver=driver, ocr_status=EarningUpload.OCRStatuses.PENDING)
                # Dispatch background task for OCR processing
                process_earning_ocr_task.delay(upload.id)
            except Driver.DoesNotExist:
                # Should not happen in normal conditions, return validation error
                raise Response({"error": "Driver profile not found."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            upload = serializer.save()
            process_earning_ocr_task.delay(upload.id)
            
    def update(self, request, *args, **kwargs):
        # Override to ensure only managers/admins can modify processed details
        if request.user.role == 'DRIVER':
            return Response({"detail": "Drivers cannot modify uploaded earnings parameters."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)
