from rest_framework import serializers
from reports.models import (
    PendingCasesReport)
from reports.serializers.case_type_serializers import CaseTypeSeralizer


class PendingCasesReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = PendingCasesReport
        fields = '__all__'  