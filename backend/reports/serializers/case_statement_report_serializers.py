from rest_framework import serializers
from reports.models import (
    Report, OldestCase, CaseType, DisposedCasesReport
)
from django.contrib.auth.models import User
from reports.serializers.case_type_serializers import CaseTypeSeralizer



class OldestCaseSeralizer(serializers.ModelSerializer):
    related_case_type = CaseTypeSeralizer(source='case_type', many=False, read_only=True)
    class Meta:
        model =OldestCase
        fields = '__all__'


class ReportSerializer(serializers.ModelSerializer):  # create class to serializer model
    creator = serializers.ReadOnlyField(source='created_by.username')
    related_casetype=CaseTypeSeralizer(source='case_type',many=False, read_only=True)
    # related_oldest_cases = serializers.SerializerMethodField()
    class Meta:
        model =Report
        fields = '__all__'
#        fields = ('id', 'desc_case', 'pnding_start_of_month', 'instituted_during_the_month', 'total_count', 'count_disposed_contested', 'count_disposed_uncontested', 'count_disposed_transferred', 'pending_in_hand', 'pending_more_then_2yrs', 'pending_more_then_4yrs', 'date_of_oldest_case', 'unit', 'no_of_working_days', 'report_year', 'report_month','remarks','is_draft','created_at','updated_at','creator')

    # def get_related_oldest_cases(self, obj):
    #     request = self.context.get('request')

    #     oldest_case = OldestCase.objects.all()

    #     report_month = request.query_params.get('report_month')
    #     report_year = request.query_params.get('report_year')
    #     creator__username =  request.query_params.get('creator__username')
    #     type_civil_criminal =request.query_params.get('civil_criminal')


    #     if type_civil_criminal:
    #         oldest_case=oldest_case.filter(case_type__desc_case=type_civil_criminal)

    #     if report_month:
    #         oldest_case=oldest_case.filter(report_month=report_month)
        
    #     if report_year:
    #         oldest_case=oldest_case.filter(report_year=report_year)

    #     if creator__username:
    #         print('User Id',creator__username )
    #         oldest_case=oldest_case.filter(created_by=creator__username)
    #     else:
    #          oldest_case=oldest_case.filter(created_by=request.user.id)

    #     return oldest_case


class BlankReportSerializer(serializers.ModelSerializer):
    report_id = serializers.IntegerField()
    pending_start_of_month = serializers.IntegerField()
    instituted_during_the_month = serializers.IntegerField()
    total_count = serializers.IntegerField()
    count_disposed_contested = serializers.IntegerField()
    count_disposed_uncontested = serializers.IntegerField()
    count_disposed_transferred = serializers.IntegerField()
    pending_in_hand = serializers.IntegerField()
    pending_more_then_2yrs = serializers.IntegerField()
    pending_more_then_4yrs = serializers.IntegerField()
    date_of_oldest_case = serializers.DateField()
    unit = serializers.IntegerField()
    no_of_working_days = serializers.IntegerField()
    report_year = serializers.IntegerField()
    report_month = serializers.CharField()
    remarks = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    is_draft = serializers.BooleanField()
    organization_id = serializers.IntegerField()
    created_by_id = serializers.IntegerField()
    updated_by_id = serializers.IntegerField()
    case_type_id = serializers.IntegerField()
    desc_case = serializers.CharField()

    class Meta:
        model = CaseType
        fields = (
    'report_id',
    'pending_start_of_month',
    'instituted_during_the_month',
    'total_count',
    'count_disposed_contested',
    'count_disposed_uncontested',
    'count_disposed_transferred',
    'pending_in_hand',
    'date_of_oldest_case',
    'pending_more_then_2yrs',
    'pending_more_then_4yrs',
    'unit',
    'no_of_working_days',
    'report_year',
    'report_month',
    'remarks',
    'created_at',
    'updated_at',
    'is_draft',
    'organization_id',
    'created_by_id',
    'updated_by_id',
    'case_type_id',
    'desc_case',

        )

class DisposedCasesReportSerializer(serializers.ModelSerializer):
    # related_casetype=CaseTypeSeralizer(source='case_type',many=False, read_only=True)
   
    class Meta:
        model = DisposedCasesReport
        fields = "__all__"




