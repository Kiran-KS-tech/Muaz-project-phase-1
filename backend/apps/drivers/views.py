from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Driver
from .serializers import DriverSerializer
from apps.accounts.permissions import IsManagerOrAbove, IsDriver


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all().order_by('-id')
    serializer_class = DriverSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'license_expiry']
    search_fields = ['name', 'driver_id', 'phone', 'license_number']
    ordering_fields = ['joining_date', 'name', 'license_expiry']

    def get_permissions(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            # Drivers can read/edit their own, managers and above can do everything
            return [permissions.IsAuthenticated()]
        return [IsManagerOrAbove()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'DRIVER':
            # Driver can only see their own profile
            return Driver.objects.filter(user=user)
        return super().get_queryset()

    @action(detail=False, methods=['get'], permission_classes=[IsDriver])
    def my_profile(self, request):
        try:
            driver = Driver.objects.get(user=request.user)
            serializer = self.get_serializer(driver)
            return Response(serializer.data)
        except Driver.DoesNotExist:
            return Response({"detail": "Driver profile not found."}, status=404)
        
    @action(detail=True, methods=['post'], permission_classes=[IsManagerOrAbove])
    def toggle_status(self, request, pk=None):
        driver = self.get_object()
        new_status = request.data.get('status')
        if new_status in Driver.Statuses.values:
            driver.status = new_status
            driver.save()
            return Response({"status": f"Status updated to {new_status}"})
        return Response({"error": "Invalid status value"}, status=400)

    @action(detail=False, methods=['post'], permission_classes=[IsManagerOrAbove])
    def ocr_license(self, request):
        license_photo = request.FILES.get('license_photo')
        if not license_photo:
            return Response({"error": "No license_photo file provided"}, status=400)

        from apps.ocr.services import OCRProcessor
        processor = OCRProcessor()
        result = processor.process_driving_license(license_photo)
        return Response(result)

