from rest_framework import serializers
from reports.models import (
    CaseType
    )   

class CaseTypeSeralizer(serializers.ModelSerializer):
    class Meta:
        model =CaseType
        fields = '__all__'