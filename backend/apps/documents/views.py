from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from .models import Document
from .serializers import DocumentSerializer
from apps.accounts.permissions import IsManagerOrAbove, IsDriver


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all().order_by('-uploaded_at')
    serializer_class = DocumentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['document_type', 'status', 'driver', 'car']
    search_fields = ['document_number']

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'DRIVER':
            # Driver can only view their own documents
            return Document.objects.filter(driver__user=user)
        return super().get_queryset()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'DRIVER':
            from apps.drivers.models import Driver
            try:
                driver = Driver.objects.get(user=user)
                serializer.save(driver=driver, status=Document.Statuses.PENDING)
            except Driver.DoesNotExist:
                serializer.save(status=Document.Statuses.PENDING)
        else:
            serializer.save()

    @action(detail=True, methods=['post'], permission_classes=[IsManagerOrAbove])
    def approve(self, request, pk=None):
        document = self.get_object()
        document.status = Document.Statuses.APPROVED
        document.save(update_fields=['status'])
        
        # If this document is associated with car fields, we can update corresponding fields on the Car model as well!
        if document.car:
            car = document.car
            if document.document_type == Document.DocumentTypes.INSURANCE:
                car.insurance_expiry = document.expiry_date
                car.insurance_number = document.document_number
            elif document.document_type == Document.DocumentTypes.PERMIT:
                car.permit_expiry = document.expiry_date
                car.permit_number = document.document_number
            elif document.document_type == Document.DocumentTypes.FITNESS:
                car.fitness_expiry = document.expiry_date
                car.fitness_number = document.document_number
            elif document.document_type == Document.DocumentTypes.POLLUTION:
                car.pollution_expiry = document.expiry_date
                car.pollution_certificate = document.document_number
            car.save()

        # Alert the driver
        if document.driver and document.driver.user:
            from apps.notifications.models import Notification
            Notification.objects.create(
                user=document.driver.user,
                title="Document Approved",
                message=f"Your document {document.get_document_type_display()} has been approved.",
                notification_type=Notification.Types.DOCUMENT_EXPIRY,
                severity=Notification.Severities.INFO
            )

        return Response({"status": "Document approved successfully."})

    @action(detail=True, methods=['post'], permission_classes=[IsManagerOrAbove])
    def reject(self, request, pk=None):
        document = self.get_object()
        document.status = Document.Statuses.REJECTED
        document.save(update_fields=['status'])

        # Alert the driver
        reason = request.data.get('reason', 'No reason provided')
        if document.driver and document.driver.user:
            from apps.notifications.models import Notification
            Notification.objects.create(
                user=document.driver.user,
                title="Document Rejected",
                message=f"Your document {document.get_document_type_display()} was rejected. Reason: {reason}.",
                notification_type=Notification.Types.DOCUMENT_EXPIRY,
                severity=Notification.Severities.CRITICAL
            )

        return Response({"status": "Document marked as rejected."})
