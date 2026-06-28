from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Car, ServiceRecord
from .serializers import CarSerializer, ServiceRecordSerializer
from apps.accounts.permissions import IsManagerOrAbove


class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all().order_by('-id')
    serializer_class = CarSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['fuel_type', 'status', 'driver_assignment']
    search_fields = ['registration_number', 'brand', 'model']
    ordering_fields = ['created_at', 'registration_number', 'insurance_expiry']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsManagerOrAbove()]

    @action(detail=True, methods=['post'], permission_classes=[IsManagerOrAbove])
    def assign_driver(self, request, pk=None):
        car = self.get_object()
        driver_id = request.data.get('driver_id')
        if driver_id:
            from apps.drivers.models import Driver
            try:
                driver = Driver.objects.get(id=driver_id)
                car.driver_assignment = driver
                car.save()
                return Response({"status": f"Driver {driver.name} assigned to car {car.registration_number}"})
            except Driver.DoesNotExist:
                return Response({"error": "Driver not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            car.driver_assignment = None
            car.save()
            return Response({"status": "Driver assignment cleared"})


class ServiceRecordViewSet(viewsets.ModelViewSet):
    queryset = ServiceRecord.objects.all().order_by('-service_date')
    serializer_class = ServiceRecordSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsManagerOrAbove()]
