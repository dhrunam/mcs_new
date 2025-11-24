from rest_framework import serializers
from accounts.models import Organization
from .organization_type_serailizers import OrganizationTypeSerializer

class OrganizationSerializer(serializers.ModelSerializer): 
    organization_type = OrganizationTypeSerializer(many=False, read_only=True)
    
    class Meta:
        model = Organization
        fields = '__all__'