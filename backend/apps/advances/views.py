from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import AdvanceRequest
from .serializers import AdvanceRequestSerializer
from apps.accounts.permissions import IsManagerOrAbove, IsDriver


class AdvanceRequestViewSet(viewsets.ModelViewSet):
    queryset = AdvanceRequest.objects.all().order_by('-request_date')
    serializer_class = AdvanceRequestSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['driver', 'status', 'request_date']

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'DRIVER':
            return AdvanceRequest.objects.filter(driver__user=user)
        return super().get_queryset()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'DRIVER':
            from apps.drivers.models import Driver
            try:
                driver = Driver.objects.get(user=user)
                serializer.save(driver=driver, status=AdvanceRequest.Statuses.PENDING)
            except Driver.DoesNotExist:
                raise Response({"error": "Driver profile not found."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer.save()

    @action(detail=True, methods=['post'], permission_classes=[IsManagerOrAbove])
    def approve(self, request, pk=None):
        advance = self.get_object()
        if advance.status != AdvanceRequest.Statuses.PENDING:
            return Response({"error": "Advance request is already resolved"}, status=400)
            
        advance.status = AdvanceRequest.Statuses.APPROVED
        advance.admin_notes = request.data.get('admin_notes', advance.admin_notes)
        advance.resolved_date = timezone.now()
        advance.save()

        # Send notification to driver
        if advance.driver.user:
            from apps.notifications.models import Notification
            Notification.objects.create(
                user=advance.driver.user,
                title="Advance Request Approved",
                message=f"Your advance request of ₹{advance.amount} has been approved. Notes: {advance.admin_notes or 'None'}",
                notification_type=Notification.Types.ADVANCE,
                severity=Notification.Severities.INFO
            )

        return Response({"status": "Advance approved successfully."})

    @action(detail=True, methods=['post'], permission_classes=[IsManagerOrAbove])
    def reject(self, request, pk=None):
        advance = self.get_object()
        if advance.status != AdvanceRequest.Statuses.PENDING:
            return Response({"error": "Advance request is already resolved"}, status=400)
            
        advance.status = AdvanceRequest.Statuses.REJECTED
        advance.admin_notes = request.data.get('admin_notes', advance.admin_notes)
        advance.resolved_date = timezone.now()
        advance.save()

        # Send notification to driver
        if advance.driver.user:
            from apps.notifications.models import Notification
            Notification.objects.create(
                user=advance.driver.user,
                title="Advance Request Rejected",
                message=f"Your advance request of ₹{advance.amount} was rejected. Notes: {advance.admin_notes or 'None'}",
                notification_type=Notification.Types.ADVANCE,
                severity=Notification.Severities.CRITICAL
            )

        return Response({"status": "Advance rejected successfully."})
