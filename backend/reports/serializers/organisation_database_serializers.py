from rest_framework import serializers
from reports.models import (
    OrganizationDatabase
    )

class OrganizationDatabaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationDatabase
        fields = '__all__'