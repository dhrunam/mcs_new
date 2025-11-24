
from rest_framework import generics, response, status, views
from reports import serializers as report_serializer, models as report_models
from rest_framework.permissions import IsAuthenticated, AllowAny

class OldestCaseDetailsRetrieve(views.APIView):
    def get(self, request,  *args, **kwargs):
        
        organization = self.request.query_params.get('organization')
        report_month = self.request.query_params.get('report_month')
        report_year = self.request.query_params.get('report_year')
        type_civil_criminal = self.request.query_params.get('civil_criminal')
        result= report_models.OldestCase.objects.all()
        if organization is not None:
            result = result.filter(organization=organization)
        
        if report_month is not None:
            result = result.filter(report_month__icontains=report_month)

        if report_year is not None:
            result = result.filter(report_year=report_year)
        if type_civil_criminal is not None:
            result = result.filter(case_type__type_civil_criminal=type_civil_criminal)

        # result = result.filter(created_by = self.request.user.id).last()
        serializer = report_serializer.OldestCaseSeralizer(result.last(), many=False)
       

        return response.Response(serializer.data,status=status.HTTP_200_OK)

class OldestCaseDetails(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = report_serializer.OldestCaseSeralizer
    queryset =report_models.OldestCase.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        request.data._mutable=True
        request.data['user'] = self.request.user.id
        request.data['updated_by'] = self.request.user.id

        return self.update(self, request, *args, **kwargs)
    
    def perform_update(self, serializer):
        serializer.save()
       
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=self.request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        
        return Response(serializer.data)
    
    def patch(self, request, *args, **kwargs):

        request.data._mutable=True
        request.data['user'] = self.request.user.id
        request.data['updated_by'] = self.request.user.id
        return self.partial_update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

