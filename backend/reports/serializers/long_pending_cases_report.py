from rest_framework import serializers
from reports.models import (
    LongPendingCasesReport
)

class LongPendingCasesReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = LongPendingCasesReport
        fields = '__all__'