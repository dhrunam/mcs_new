from rest_framework import serializers
from reports.models import (
    ExParteInjunctionCasesReport
    )
from reports.serializers.case_type_serializers import CaseTypeSeralizer


class ExParteInjunctionCasesReportSerializer(serializers.ModelSerializer):
    # related_casetype=CaseTypeSeralizer(source='case_type',many=False, read_only=True)
   
    class Meta:
        model = ExParteInjunctionCasesReport
        fields = '__all__'