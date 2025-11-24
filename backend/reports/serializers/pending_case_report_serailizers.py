from rest_framework import serializers
from reports.models import (
    PendingCasesReport)

class PendingCasesReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = PendingCasesReport
        fields = '__all__'  