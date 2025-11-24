from rest_framework import generics, status, response
from reports  import serializers as report_serializer, models as report_models
import csv
from io import StringIO
from datetime import timezone
from rest_framework.permissions import IsAuthenticated

class ListOfUndertrialPrisonersList(generics.ListCreateAPIView):
    queryset = report_models.ListOfUndertrialPrisoners.objects.all().order_by('-id')
    serializer_class = report_serializer.ListOfUndertrialPrisonersSerializer

    def create(self, request, *args, **kwargs):
        file = request.FILES.get('undertrial_prisoner_report')

        if not file:
            return response.Response({"error": "CSV file is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            file_data = file.read().decode('utf-8')
            csv_reader = csv.DictReader(StringIO(file_data))
            
            records = []
            for row in csv_reader:
                row['report_year'] = self.request.data.get('report_year')
                row['report_month'] = self.request.data.get('report_month')
                row['organization']=self.request.data.get('organization')
                row['created_by'] = request.user.id  # Add user ID

                # row['created_at'] = timezone.now()  # Add current timestamp
                serializer = self.get_serializer(data=row)
                serializer.is_valid(raise_exception=True)
                records.append(Record(**serializer.validated_data))
            
            report_models.ListOfUndertrialPrisoners.objects.bulk_create(records)
            return response.Response({"message": f"{len(records)} records successfully added."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return response.Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

 