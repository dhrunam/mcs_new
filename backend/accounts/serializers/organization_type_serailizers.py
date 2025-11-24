from rest_framework import serializers
from accounts.models import OrganizationType

class OrganizationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationType
        fields = '__all__'