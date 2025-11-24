from rest_framework import serializers
from reports.models import (
    StatementOfCourtFeesFines)

class StatementOfCourtFeesFinesSerializer(serializers.ModelSerializer):
    class Meta:
        model =StatementOfCourtFeesFines
        fields = '__all__'