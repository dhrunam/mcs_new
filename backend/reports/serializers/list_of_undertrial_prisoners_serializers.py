from rest_framework import serializers
from reports.models import (
    ListOfUndertrialPrisoners
)

class ListOfUndertrialPrisonersSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListOfUndertrialPrisoners
        fields = '__all__'
