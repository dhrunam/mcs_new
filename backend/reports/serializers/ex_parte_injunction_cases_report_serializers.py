from rest_framework import serializers
from reports.models import (
    ExParteInjunctionCasesReport
    )
class ExParteInjunctionCasesReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExParteInjunctionCasesReport
        fields = '__all__'