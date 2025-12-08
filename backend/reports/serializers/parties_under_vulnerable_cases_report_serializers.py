from rest_framework import serializers
from reports.models import (
    PartiesUnderVulnerableGroupCasesReport
)   

class PartiesUnderVulnerableCasesReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartiesUnderVulnerableGroupCasesReport
        fields = '__all__'