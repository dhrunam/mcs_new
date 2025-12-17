from rest_framework import generics, response, status
from reports import serializers as report_serializer, models as report_models
from rest_framework.permissions import IsAuthenticated

class CaseTypeList(generics.ListCreateAPIView):
    serializer_class = report_serializer.CaseTypeSeralizer
    queryset = report_models.CaseType.objects.all()
    # permission_classes = [IsAuthenticated]
    # pagination_class = CustomPagination

    def get_queryset(self):
        queryset = report_models.CaseType.objects.all()
        court_type= self.request.query_params.get('court_type')
        if court_type:
            filter_kwargs = {court_type: True}
            queryset = queryset.filter(**filter_kwargs)

        return queryset
    
class CaseTypeListAll(generics.ListAPIView):
    serializer_class = report_serializer.CaseTypeSeralizer
    queryset = report_models.CaseType.objects.all()
    pagination_class=None
    # permission_classes = [IsAuthenticated]
    # pagination_class = CustomPagination   

    def get_queryset(self):
        queryset = report_models.CaseType.objects.all()
        court_type= self.request.query_params.get('court_type')
        if court_type:
            filter_kwargs = {court_type: True}
            queryset = queryset.filter(**filter_kwargs)

        return queryset

