from rest_framework import serializers
from reports.models import (
    PendingCasesPartiesAboveSixty
)
from reports.serializers.case_type_serializers import CaseTypeSeralizer

class PendingCasesPartiesAboveSixtySerializer(serializers.ModelSerializer):
    class Meta:
        model = PendingCasesPartiesAboveSixty
        fields = '__all__'  