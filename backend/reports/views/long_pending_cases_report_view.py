from rest_framework import generics, status, response
from reports  import serializers as report_serializer, models as report_models
import csv
from io import StringIO
from datetime import timezone
from rest_framework.permissions import IsAuthenticated

class LongPendingCasesReportList(generics.ListCreateAPIView):
    queryset = report_models.LongPendingCasesReport.objects.all().order_by('-id')
    serializer_class = report_serializer.LongPendingCasesReportSerializer

    def create(self, request, *args, **kwargs):
       
        try:
            file = request.FILES.get('file')

            if not file:
                return response.Response({"error": "CSV file is required."}, status=status.HTTP_400_BAD_REQUEST)

            file_data = file.read().decode('utf-8')
            csv_reader = csv.DictReader(StringIO(file_data))
            profile = getattr(self.request.user, "user_profile", None)
            model =report_models.LongPendingCasesReport
            records = []
            for row in csv_reader:
                row['report_year'] = self.request.data.get('report_year')
                row['report_month'] = self.request.data.get('report_month')
                row['organization']= profile.organization_id if profile and profile.organization_id else None
                row['created_by'] = request.user.id  # Add user ID

                # row['created_at'] = timezone.now()  # Add current timestamp
                serializer = self.get_serializer(data=row)
                serializer.is_valid(raise_exception=True)
                records.append(model(**serializer.validated_data))
            
            report_models.StatementOfCourtFeesFines.objects.bulk_create(records)
            return response.Response({"message": f"{len(records)} records successfully added."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return response.Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        
        queryset = self.queryset

        report_month = self.request.query_params.get('report_month')
        report_year = self.request.query_params.get('report_year')
        # creator__username =  self.request.query_params.get('creator__username')
        type_civil_criminal = self.request.query_params.get('civil_criminal')
        # organization =  self.request.query_params.get('organization')
        profile = getattr(self.request.user, "user_profile", None)
        org_id = profile.organization_id if profile and profile.organization_id else None
        if report_month:
            queryset =queryset.filter( report_month=report_month)
        if report_year:
            queryset =queryset.filter( report_year=report_year)
        if type_civil_criminal:
            queryset =queryset.filter( civil_criminal=type_civil_criminal)
        if org_id:
            queryset =queryset.filter( organization_id=org_id)  
        
        return queryset
    

class LongPendingCasesReportListGetForHCS(generics.ListAPIView):
    queryset = report_models.LongPendingCasesReport.objects.all().order_by('-id')
    serializer_class = report_serializer.LongPendingCasesReportSerializer

    def get_queryset(self):
        
        queryset = self.queryset

        report_month = self.request.query_params.get('report_month')
        report_year = self.request.query_params.get('report_year')
        # creator__username =  self.request.query_params.get('creator__username')
        type_civil_criminal = self.request.query_params.get('civil_criminal')
        org_id =  self.request.query_params.get('organization')

        if report_month:
            queryset =queryset.filter( report_month=report_month)
        if report_year:
            queryset =queryset.filter( report_year=report_year)
        if type_civil_criminal:
            queryset =queryset.filter( civil_criminal=type_civil_criminal)
        if org_id:
            queryset =queryset.filter( organization_id=org_id)  
        
        return queryset
    
class LastUploadedLongPendingCasesReportList(generics.ListAPIView):
    queryset = report_models.LongPendingCasesReport.objects.all().order_by('-id')
    serializer_class = report_serializer.LongPendingCasesReportSerializer

    def get_queryset(self):
        from django.db.models import Max

        profile = getattr(self.request.user, "user_profile", None)
        org_id = profile.organization_id if profile and profile.organization_id else None
    
        latest_time = self.queryset.aggregate(Max('created_at'))['created_at__max']
        self.queryset = self.queryset.filter(organization_id=org_id, created_at=latest_time)
        return self.queryset    
    

    