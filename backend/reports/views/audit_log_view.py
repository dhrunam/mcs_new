from rest_framework import generics, response, status
from reports import serializers as report_serializer, models as report_models
from auditlog.models import LogEntry
from rest_framework.permissions import IsAuthenticated
from reports.serializers.audit_log_entry_serializers import AuditLogEntrySerializer

class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogEntrySerializer
    queryset = LogEntry.objects.all()
    permission_classes = [IsAuthenticated]

