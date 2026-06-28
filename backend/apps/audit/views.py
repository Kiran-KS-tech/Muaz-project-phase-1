from rest_framework import viewsets, mixins
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from .models import AuditLog
from .serializers import AuditLogSerializer
from apps.accounts.permissions import IsSuperAdminOrOwner


class AuditLogViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = AuditLog.objects.all().order_by('-timestamp')
    serializer_class = AuditLogSerializer
    permission_classes = [IsSuperAdminOrOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['action', 'model_name', 'user']
    search_fields = ['object_id', 'ip_address']
