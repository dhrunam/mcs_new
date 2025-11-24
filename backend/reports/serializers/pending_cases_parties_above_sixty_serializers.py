from rest_framework import serializers
from reports.models import (
    PendingCasesPartiesAboveSixty
)

class PendingCasesPartiesAboveSixtySerializer(serializers.ModelSerializer):
    class Meta:
        model = PendingCasesPartiesAboveSixty
        fields = '__all__'  