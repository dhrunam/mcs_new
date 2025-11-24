from rest_framework import generics, response, status
from reports import serializers as report_serializer, models as report_models, utility
from rest_framework.permissions import IsAuthenticated, AllowAny

class OrganizationDatabaseList(generics.ListCreateAPIView):
    serializer_class = report_serializer.OrganizationDatabaseSerializer
    queryset = report_models.OrganizationDatabase.objects.all()
    permission_classes = [AllowAny]
  
    # def get_queryset(self):
    #     queryset = report_models.OrganizationDatabase.objects.all()
    #     org_id=utility.get_organization_id(self.request)
    #     if org_id:
            
    #         queryset = queryset.filter(organisation=org_id)

    #     return queryset

class OrganizationDatabaseDetails(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = report_serializer.OrganizationDatabaseSerializer
    queryset = report_models.OrganizationDatabase.objects.all()
    permission_classes = [AllowAny]

