from rest_framework import views, response
from reports import serializers as report_serializer, models as report_models
from django.db.models import Sum, Q, F, Value, OuterRef, Subquery, Case, When, IntegerField, CharField
from django.db.models.functions import Coalesce
# Monthly Summary Report by Organization
class ReportNoteSheetApiView(views.APIView):

    def get(self, request, *args, **kwargs):
        organization_id = request.query_params.get('organization', 19)  # Default organization id
        report_year = request.query_params.get('report_year', 2023)  # Default report year
        report_month = request.query_params.get('report_month', 'jan')  # Default report month

        # Function to create a queryset with conditional annotations
        def get_report_queryset(type_civil_criminal, type_main_mis):
            return report_models.Report.objects.filter(
                is_draft=False,
                report_year=report_year,
                report_month__icontains=report_month,
                organization_id=organization_id,
                case_type__type_civil_criminal=type_civil_criminal,
                case_type__type_main_mis=type_main_mis
            ).values('organization_id').annotate(
                count_disposed_contested=Coalesce(Sum('count_disposed_contested'), Value(0)),
                count_disposed_uncontested=Coalesce(Sum('count_disposed_uncontested'), Value(0)),
                pending_in_hand=Coalesce(Sum('pending_in_hand'), Value(0)),
                type_civil_criminal=Value(type_civil_criminal, output_field=CharField()),
                type_main_mis=Value(type_main_mis, output_field=CharField())
            )

        # Civil - Main
        civil_main = get_report_queryset('civil', 'main')

        # Civil - Misc
        civil_misc = get_report_queryset('civil', 'misc')

        # Criminal - Main
        criminal_main = get_report_queryset('criminal', 'main')

        # Criminal - Misc
        criminal_misc = get_report_queryset('criminal', 'misc')

        # Combine all queries using union (like SQL UNION)
        # combined_reports = civil_main.union(civil_misc, criminal_main, criminal_misc)
        # main_report = list(combined_reports)

      
        notesheet_stats = report_models.Report.objects.filter(
            report_year=report_year,
            report_month__icontains=report_month,
            organization_id=organization_id,
            is_draft=False
        ).aggregate(
            total_cases_pending=Sum('pending_in_hand'),
            total_unit_earned=Sum('unit')
        )

        result= report_models.OldestCase.objects.all()
        # result = result.filter(case_type__type_civil_criminal='civil' )
        if organization_id is not None:
            result = result.filter(organization=organization_id )
        
        if report_month is not None:
            result = result.filter(report_month__icontains=report_month)

        if report_year is not None:
            result = result.filter(report_year=report_year)

        # result = result.filter(created_by = self.request.user.id).last()
        result_civil = result.filter(case_type__type_civil_criminal='civil')
        result_criminal = result.filter(case_type__type_civil_criminal='criminal')
        serializer_civil = report_serializer.OldestCaseSeralizer(result_civil.last(), many=False)
        serializer_criminal=report_serializer.OldestCaseSeralizer(result_criminal.last(), many=False)
        civil_main_single = civil_main.order_by('organization_id').last()
        civil_misc_single = civil_misc.order_by('organization_id').last()
        criminal_main_single= criminal_main.order_by('organization_id').last()
        criminal_misc_single = criminal_misc.order_by('organization_id').last()
        return  response.Response({
            
                        'civil_main_single':civil_main_single,
                        'civil_misc_single':civil_misc_single,
                        'criminal_main_single': criminal_main_single,
                        'criminal_misc_single':criminal_misc_single,
                        'notesheet_stats':notesheet_stats,
                        'oldest_cases_civil':serializer_civil.data,
                        'oldest_cases_criminal': serializer_criminal.data
                         
                         })

