from rest_framework import serializers
from reports.models import (
    LongPendingCasesReport
)
from reports.serializers.case_type_serializers import CaseTypeSeralizer



class LongPendingCasesReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = LongPendingCasesReport
        fields = '__all__'