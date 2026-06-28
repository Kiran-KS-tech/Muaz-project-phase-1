from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import datetime
from .models import Settlement
from .serializers import SettlementSerializer
from .tasks import generate_settlements_for_range
from apps.accounts.permissions import IsManagerOrAbove


class SettlementViewSet(viewsets.ModelViewSet):
    queryset = Settlement.objects.all().order_by('-start_date')
    serializer_class = SettlementSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['driver', 'status', 'start_date']

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'DRIVER':
            return Settlement.objects.filter(driver__user=user)
        return super().get_queryset()

    @action(detail=True, methods=['post'], permission_classes=[IsManagerOrAbove])
    def approve(self, request, pk=None):
        settlement = self.get_object()
        settlement.status = Settlement.Statuses.APPROVED
        settlement.save(update_fields=['status'])
        
        if settlement.driver.user:
            from apps.notifications.models import Notification
            Notification.objects.create(
                user=settlement.driver.user,
                title="Settlement Approved",
                message=f"Your settlement for {settlement.start_date} to {settlement.end_date} of ₹{settlement.final_settlement_amount} has been approved. Payout is being processed.",
                notification_type=Notification.Types.SETTLEMENT,
                severity=Notification.Severities.INFO
            )
        return Response({"status": "Settlement approved."})

    @action(detail=True, methods=['post'], permission_classes=[IsManagerOrAbove])
    def pay(self, request, pk=None):
        settlement = self.get_object()
        ref = request.data.get('payment_reference')
        if not ref:
            return Response({"error": "Payment reference is required"}, status=400)
            
        settlement.status = Settlement.Statuses.PAID
        settlement.payment_reference = ref
        settlement.paid_at = timezone.now()
        settlement.save()

        if settlement.driver.user:
            from apps.notifications.models import Notification
            Notification.objects.create(
                user=settlement.driver.user,
                title="Settlement Paid",
                message=f"Your settlement for {settlement.start_date} to {settlement.end_date} of ₹{settlement.final_settlement_amount} has been paid. Ref: {ref}.",
                notification_type=Notification.Types.SETTLEMENT,
                severity=Notification.Severities.INFO
            )
        return Response({"status": "Settlement marked as PAID."})

    @action(detail=True, methods=['post'], permission_classes=[IsManagerOrAbove])
    def adjust(self, request, pk=None):
        settlement = self.get_object()
        adjustment = request.data.get('manual_adjustment')
        reason = request.data.get('manual_adjustment_reason')
        
        if adjustment is None:
            return Response({"error": "manual_adjustment value is required"}, status=400)

        try:
            settlement.manual_adjustment = float(adjustment)
            settlement.manual_adjustment_reason = reason
            settlement.save()  # Auto-recalculates final settlement amount
            return Response({
                "status": "Adjustment applied successfully.",
                "final_settlement_amount": settlement.final_settlement_amount
            })
        except ValueError:
            return Response({"error": "Invalid adjustment amount format"}, status=400)

    @action(detail=False, methods=['post'], permission_classes=[IsManagerOrAbove])
    def generate_range(self, request):
        start_str = request.data.get('start_date')
        end_str = request.data.get('end_date')

        if not start_str or not end_str:
            return Response({"error": "start_date and end_date are required (YYYY-MM-DD)"}, status=400)

        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Dates must be in YYYY-MM-DD format"}, status=400)

        result = generate_settlements_for_range(start_date, end_date)
        return Response({"status": result})
