from django_filters import rest_framework as filters
from .models import Report


# We create filters for each field we want to be able to filter on
class ReportFilter(filters.FilterSet):
    report_month = filters.CharFilter(lookup_expr='icontains')
    report_year = filters.NumberFilter()
    desc_case = filters.CharFilter(lookup_expr='icontains')
    creator__username = filters.CharFilter(lookup_expr='icontains')
    is_draft=filters.BooleanFilter(field_name='is_draft',lookup_expr='exact')

    class Meta:
        model = Report
        fields = ['report_month', 'report_year','desc_case','creator__username','is_draft']

