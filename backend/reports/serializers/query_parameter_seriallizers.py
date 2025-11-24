from rest_framework import serializers

class CaseStatementReportQueryParameterSerializer(serializers.Serializer):
    
    # last_month_end_date = serializers.DateField(required=True)
    # present_month_start_date = serializers.DateField(required=True)
    # present_month_end_date = serializers.DateField(required=True)
    month = serializers.IntegerField(required=True)
    year = serializers.IntegerField(required= True)
    criminal_civil_flag = serializers.ChoiceField(choices=['1', '2'], required=True)

class MonthlyFeeCollectionReportQueryParameterSerializer(serializers.Serializer):
    
    # last_month_end_date = serializers.DateField(required=True)
    # present_month_start_date = serializers.DateField(required=True)
    # present_month_end_date = serializers.DateField(required=True)
    month = serializers.IntegerField(required=True)
    year = serializers.IntegerField(required= True)
   

