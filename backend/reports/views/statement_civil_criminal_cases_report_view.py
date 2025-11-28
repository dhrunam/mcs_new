from rest_framework import generics, response, status, views
from reports import serializers as report_serializer, models as report_models, utility
from accounts import models as auth_models
from django.db.models import Sum, Q, F, Value, OuterRef, Subquery, Case, When, IntegerField, CharField
from django.db.models.functions import Coalesce

from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction, connections
from rest_framework import exceptions
from datetime import timedelta, datetime
import calendar

class ListCreateReportAPIView(generics.ListCreateAPIView):
    serializer_class = report_serializer.ReportSerializer
    queryset = report_models.Report.objects.all()
    # permission_classes = [IsAuthenticated]
    # pagination_class = CustomPagination
    # pagination_class = None
    # filter_backends = (filters.DjangoFilterBackend,)
    # filterset_class = ReportFilter
    
    # def create(self,request,*args,**kwargs):
    #     serializer = self.get_serializer(data=request.data, many=True)
    #     serializer.is_valid(raise_exception=True)
    #     reports=serializer.save(creator=self.request.user)
    #     return Response(serializer.data,status=status.HTTP_201_CREATED)


    # def perform_create(self,serializer):
    #     # Assign the user who created the Report
    #     serializer = self.get_serializer(data=self.request.data, many=True)
    #     if serializer.is_valid():
    #         serializer.save(creator=self.request.user)
    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        try:
        
            pass
        
        except :
            pass

        data= request.data
        print('data:', data)
        report_data = request.data.get('report')
        print('report_data:', report_data)
        oldestcase_data = request.data.get('oldest_case')
        print('oldestcase_data:', oldestcase_data)
        # Check if data is a list
        if not isinstance(report_data, list):
            return response.Response({'error': 'Expected a list of records'}, status=status.HTTP_400_BAD_REQUEST)

        # Separate records into create and update lists
        create_list = []
        update_list = []
        user_profile= auth_models.UserProfile.objects.filter(user=self.request.user.id).last()
        # Assuming each record has a unique 'id' field for updates
        for record in report_data:
            record['created_by']= self.request.user.id
            record['case_type']=  record['case_type_id']
            if user_profile:
                record['organization']= user_profile.organization.id

            # if 'case_type_id' and 'report_year' and 'report_month' and 'organization' in record:
            if record['id']==0:
                print('Insert..')
                create_list.append(record)
               
            else:
                print('Update..')
                update_list.append(record)


        # Bulk create

        if len(create_list)>1:
            print('records update_list:', create_list)
            create_serializer =  self.get_serializer(data=create_list, many=True)
            if create_serializer.is_valid():

                create_serializer.save()
            else:
                return Response(create_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Bulk update
        if len(update_list)>1:
            print('records:', update_list)
            for record in update_list:
                
                try:
                    # instance = Report.objects.get(desc_case_id=record['desc_case_id'],
                    #                             report_year=record['report_year'], 
                    #                             report_month=record['report_month'], 
                    #                             organization=record['organization'],
                                                
                    #                                 )
                    instance = report_models.Report.objects.get( id=record['id']
                                                
                                                    )
                    serializer =  self.get_serializer(instance, data=record, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except report_models.Report.DoesNotExist:
                    return response.Response({'error': f'Record with id {record["id"]} does not exist'}, status=status.HTTP_404_NOT_FOUND)

       
        if oldestcase_data and oldestcase_data['case_type']:
            report_models.OldestCase.objects.update_or_create(
                organization= auth_models.Organization.objects.get(id=oldestcase_data['organization']),
                report_year = oldestcase_data['report_year'], 
                report_month= oldestcase_data['report_month'],
                case_type = report_models.CaseType.objects.get(id=oldestcase_data['case_type'])  ,
                defaults={
                'case_no' : oldestcase_data['case_no'],
                'petitioner' : oldestcase_data['petitioner'],
                'responder' : oldestcase_data['responder'],
                'remarks' : oldestcase_data['remarks'],
                'date_of_inst' : oldestcase_data['date_of_inst'],
                'status': oldestcase_data['status'],
                'created_by' : self.request.user
                }
              
   
            )
       
        return response.Response({'status': 'success'}, status=status.HTTP_200_OK)


    def get_queryset(self):
        queryset = report_models.Report.objects.all()
        print("Just queried..:", queryset)
        print('I am called..')
        is_draft = self.request.query_params.get('is_draft')
        report_month = self.request.query_params.get('report_month')
        report_year = self.request.query_params.get('report_year')
        creator__username =  self.request.query_params.get('creator__username')
        type_civil_criminal = self.request.query_params.get('civil_criminal')
        organization =  self.request.query_params.get('organization')

        if type_civil_criminal:
            queryset=queryset.filter(case_type__type_civil_criminal=type_civil_criminal)

        if is_draft:
            queryset=queryset.filter(is_draft=is_draft)

        if report_month:
            queryset=queryset.filter(report_month=report_month)
        
        if report_year:
            queryset=queryset.filter(report_year=report_year)

        if creator__username:
            print('User Id',creator__username )
            queryset=queryset.filter(created_by=creator__username)
        else:
             queryset=queryset.filter(created_by=self.request.user.id)
        
        if organization:
            queryset=queryset.filter(organization = organization)

        print("Before.. return:", queryset)

        return queryset
    
     # Override get_serializer_context to pass the request to the serializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            'request': self.request  # Pass the request to the serializer
        })
        return context
    
    def get_report_query(self, request, *args, **kwargs):

        report_subquery = report_models.Report.objects.all()
        
        is_draft = self.request.query_params.get('is_draft')

        report_month = self.request.query_params.get('report_month')
        report_year = self.request.query_params.get('report_year')
        creator__username =  self.request.query_params.get('creator__username')
        type_civil_criminal = self.request.query_params.get('civil_criminal')
        organization =  self.request.query_params.get('organization')

        if type_civil_criminal:
            print('civil_criminal',type_civil_criminal)
            report_subquery=report_subquery.filter(case_type__type_civil_criminal=type_civil_criminal)
            

        if is_draft:
            report_subquery=report_subquery.filter(is_draft=is_draft)

        if report_month:
            report_subquery=report_subquery.filter(report_month=report_month)
        
        if report_year:
            report_subquery=report_subquery.filter(report_year=report_year)

        if creator__username:
            print('User Id',creator__username )
            report_subquery=report_subquery.filter(created_by=creator__username)
        else:
             report_subquery=report_subquery.filter(created_by=self.request.user.id)
        
        if organization:
            report_subquery=report_subquery.filter(organization = organization)

        print('report_subquery:', report_subquery)
        return report_subquery
    
    def get_casetype_query(self, request, *args, **kwargs):
        queryset = report_models.CaseType.objects.all()
        print('Just after call..:', queryset)
        type_civil_criminal = self.request.query_params.get('civil_criminal')
        print('Type Civil Criminal..', type_civil_criminal)
        user_profile = self.request.user.user_profile
        print('User Profile..', user_profile)
        org_type_short_name= user_profile.organization.organization_type.org_type_short_name

        if type_civil_criminal:
              queryset = queryset.filter(type_civil_criminal=type_civil_criminal)
              print('After type civil criminal call..:', queryset)

        if org_type_short_name:
            if org_type_short_name=='hcs':
                creator__username =  self.request.query_params.get('creator__username')
                org_type_short_name = auth_models.UserProfile.objects.filter(user=creator__username).last().organization.organization_type.org_type_short_name
                # print('Case Type:', queryset)
                # return queryset
            filter_kwargs = {org_type_short_name: True}
            queryset = queryset.filter(**filter_kwargs)

        print('Before after call..:', queryset)

        return queryset
    
    
    def get(self, request, *args, **kwargs):

        # Custom queryset logic
       
        # Subquery to filter based on year and month
        report_subquery = self.get_report_query(self, request, *args, **kwargs).filter(case_type=OuterRef('pk')).values(
            'id',
            'case_type',
            'pending_start_of_month', 
            'instituted_during_the_month', 
            'total_count',
            'count_disposed_contested', 
            'count_disposed_uncontested', 
            'count_disposed_transferred',
            'pending_in_hand', 
            'pending_more_then_2yrs', 
            'pending_more_then_4yrs', 
            'date_of_oldest_case',
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
            'updated_by_id'
        )[:1]  # Ensures we only get one record

        # Query the CaseType with the subquery
        queryset = self.get_casetype_query(self, request, *args, **kwargs).annotate(
            report_id=Coalesce(Subquery(report_subquery.values('id')),Value(0)),
            pending_start_of_month=Coalesce(Subquery(report_subquery.values('pending_start_of_month')), Value(0)),
            instituted_during_the_month=Coalesce(Subquery(report_subquery.values('instituted_during_the_month')), Value(0)),
            total_count=Coalesce(Subquery(report_subquery.values('total_count')), Value(0)),
            count_disposed_contested=Coalesce(Subquery(report_subquery.values('count_disposed_contested')), Value(0)),
            count_disposed_uncontested=Coalesce(Subquery(report_subquery.values('count_disposed_uncontested')), Value(0)),
            count_disposed_transferred=Coalesce(Subquery(report_subquery.values('count_disposed_transferred')), Value(0)),
            pending_in_hand=Coalesce(Subquery(report_subquery.values('pending_in_hand')), Value(0)),
            pending_more_then_2yrs=Coalesce(Subquery(report_subquery.values('pending_more_then_2yrs')), Value(0)),
            pending_more_then_4yrs=Coalesce(Subquery(report_subquery.values('pending_more_then_4yrs')), Value(0)),
            date_of_oldest_case=Subquery(report_subquery.values('date_of_oldest_case')),
            unit=Coalesce(Subquery(report_subquery.values('unit')), Value(0)),
            no_of_working_days=Coalesce(Subquery(report_subquery.values('no_of_working_days')), Value(0)),
            report_year=Subquery(report_subquery.values('report_year')),
            report_month=Subquery(report_subquery.values('report_month')),
            remarks=Subquery(report_subquery.values('remarks')),
            created_at=Subquery(report_subquery.values('created_at')),
            updated_at=Subquery(report_subquery.values('updated_at')),
            is_draft=Coalesce( Subquery(report_subquery.values('is_draft')), Value(True)),
            organization_id=Subquery(report_subquery.values('organization_id')),
            created_by_id=Subquery(report_subquery.values('created_by_id')),
            updated_by_id=Subquery(report_subquery.values('updated_by_id')),
            case_type_id=F('id'),
            # desc_case=F('desc_case')
        )

        print('Last Result', queryset)
        # Serialize the queryset
        # serializer = self.get_serializer(queryset, many=True)
        serializer =report_serializer.BlankReportSerializer(queryset, many=True)
        
        # Return response with serialized data
        return response.Response(serializer.data, status=status.HTTP_200_OK)




class RetrieveUpdateDestroyReportAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = report_serializer.ReportSerializer
    queryset =report_models.Report.objects.all()

class MonthlyReportForAdmin(generics.ListAPIView):

    serializer_class = report_serializer.ReportSerializer
    queryset = report_models.Report.objects.all()

    def get_report_query(self, request, *args, **kwargs):

        report_subquery = report_models.Report.objects.all()
        
        is_draft = self.request.query_params.get('is_draft')

        report_month = self.request.query_params.get('report_month')
        report_year = self.request.query_params.get('report_year')
        creator__username =  self.request.query_params.get('creator__username')
        type_civil_criminal = self.request.query_params.get('civil_criminal')
        organization =  self.request.query_params.get('organization')

        if type_civil_criminal:
            print('civil_criminal',type_civil_criminal)
            report_subquery=report_subquery.filter(case_type__type_civil_criminal=type_civil_criminal)
            

        if is_draft:
            report_subquery=report_subquery.filter(is_draft=is_draft)

        if report_month:
            report_subquery=report_subquery.filter(report_month=report_month)
        
        if report_year:
            report_subquery=report_subquery.filter(report_year=report_year)

        if creator__username:
            print('User Id',creator__username )
            report_subquery=report_subquery.filter(created_by=creator__username)
        else:
             report_subquery=report_subquery.filter(created_by=self.request.user.id)
        
        if organization:
            report_subquery=report_subquery.filter(organization = organization)

        return report_subquery
    
    def get_casetype_query(self, request, *args, **kwargs):
        queryset = report_models.CaseType.objects.all()
        type_civil_criminal = self.request.query_params.get('civil_criminal')
        user_profile = self.request.user.user_profile
        org_type_short_name= ''
       
        if 'highcourt_user'  in self.request.user.groups:
            return queryset

        if type_civil_criminal:
              queryset = queryset.filter(type_civil_criminal=type_civil_criminal)

        if org_type_short_name:
            if org_type_short_name=='hcs':
                return queryset
            filter_kwargs = {org_type_short_name: True}
            queryset = queryset.filter(**filter_kwargs)

        return queryset
    
    
    def get(self, request, *args, **kwargs):

        # Custom queryset logic
       
        # Subquery to filter based on year and month
        report_subquery = self.get_report_query(self, request, *args, **kwargs).filter(case_type=OuterRef('pk')).values(
            'id',
            'case_type',
            'pending_start_of_month', 
            'instituted_during_the_month', 
            'total_count',
            'count_disposed_contested', 
            'count_disposed_uncontested', 
            'count_disposed_transferred',
            'pending_in_hand', 
            'pending_more_then_2yrs', 
            'pending_more_then_4yrs', 
            'date_of_oldest_case',
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
            'updated_by_id'
        )[:1]  # Ensures we only get one record

        # Query the CaseType with the subquery
        queryset = self.get_casetype_query(self, request, *args, **kwargs).annotate(
            report_id=Coalesce(Subquery(report_subquery.values('id')),Value(0)),
            pending_start_of_month=Coalesce(Subquery(report_subquery.values('pending_start_of_month')), Value(0)),
            instituted_during_the_month=Coalesce(Subquery(report_subquery.values('instituted_during_the_month')), Value(0)),
            total_count=Coalesce(Subquery(report_subquery.values('total_count')), Value(0)),
            count_disposed_contested=Coalesce(Subquery(report_subquery.values('count_disposed_contested')), Value(0)),
            count_disposed_uncontested=Coalesce(Subquery(report_subquery.values('count_disposed_uncontested')), Value(0)),
            count_disposed_transferred=Coalesce(Subquery(report_subquery.values('count_disposed_transferred')), Value(0)),
            pending_in_hand=Coalesce(Subquery(report_subquery.values('pending_in_hand')), Value(0)),
            pending_more_then_2yrs=Coalesce(Subquery(report_subquery.values('pending_more_then_2yrs')), Value(0)),
            pending_more_then_4yrs=Coalesce(Subquery(report_subquery.values('pending_more_then_4yrs')), Value(0)),
            date_of_oldest_case=Subquery(report_subquery.values('date_of_oldest_case')),
            unit=Coalesce(Subquery(report_subquery.values('unit')), Value(0)),
            no_of_working_days=Coalesce(Subquery(report_subquery.values('no_of_working_days')), Value(0)),
            report_year=Subquery(report_subquery.values('report_year')),
            report_month=Subquery(report_subquery.values('report_month')),
            remarks=Subquery(report_subquery.values('remarks')),
            created_at=Subquery(report_subquery.values('created_at')),
            updated_at=Subquery(report_subquery.values('updated_at')),
            is_draft=Coalesce( Subquery(report_subquery.values('is_draft')), Value(True)),
            organization_id=Subquery(report_subquery.values('organization_id')),
            created_by_id=Subquery(report_subquery.values('created_by_id')),
            updated_by_id=Subquery(report_subquery.values('updated_by_id')),
            case_type_id=F('id'),
            # desc_case=F('desc_case')
        )

        # Serialize the queryset
        # serializer = self.get_serializer(queryset, many=True)
        serializer =report_serializer.BlankReportSerializer(queryset, many=True)
        
        # Return response with serialized data
        return response.Response(serializer.data, status=status.HTTP_200_OK)


class ReportSummaryView(views.APIView):
    def get(self, request, *args, **kwargs):
        # Query for the 'misc' case type with 'civil' category
        print('Here I am..')
        year = self.request.query_params.get('year')
        month = self.request.query_params.get('month')
        result = []
        civil_misc_query = report_models.Report.objects.filter(
            case_type__type_main_mis='misc',
            case_type__type_civil_criminal='civil',
            report_year=year,
            report_month__icontains= month
        ).values('organization__id', 'organization__organization_shortname').annotate(
            civil_pending_start_of_month=Sum('pending_start_of_month'),
            civil_instituted_during_the_month=Sum('instituted_during_the_month'),
            civil_total_count=Sum('total_count'),
            civil_count_disposed_contested=Sum('count_disposed_contested'),
            civil_count_disposed_uncontested=Sum('count_disposed_uncontested'),
            civil_count_disposed_transferred=Sum('count_disposed_transferred'),
            civil_pending_in_hand=Sum('pending_in_hand'),
            civil_pending_more_than_2yrs=Sum('pending_more_then_2yrs'),
            civil_pending_more_than_4yrs=Sum('pending_more_then_4yrs'),
            civil_unit=Sum('unit'),
            civil_no_of_working_days=Sum('no_of_working_days')
        )

          # Query for the 'main' case type with 'civil' category
        civil_main_query = report_models.Report.objects.filter(
            case_type__type_main_mis='main',
            case_type__type_civil_criminal='civil',
            report_year=year,
            report_month__icontains=month
        ).values('organization__id', 'organization__organization_shortname').annotate(
            civil_pending_start_of_month=Sum('pending_start_of_month'),
            civil_instituted_during_the_month=Sum('instituted_during_the_month'),
            civil_total_count=Sum('total_count'),
            civil_count_disposed_contested=Sum('count_disposed_contested'),
            civil_count_disposed_uncontested=Sum('count_disposed_uncontested'),
            civil_count_disposed_transferred=Sum('count_disposed_transferred'),
            civil_pending_in_hand=Sum('pending_in_hand'),
            civil_pending_more_than_2yrs=Sum('pending_more_then_2yrs'),
            civil_pending_more_than_4yrs=Sum('pending_more_then_4yrs'),
            civil_unit=Sum('unit'),
            civil_no_of_working_days=Sum('no_of_working_days')
        )

        # Query for the 'main' case type with 'criminal' category
        criminal_main_query =report_models.Report.objects.filter(
            case_type__type_main_mis='main',
            case_type__type_civil_criminal='criminal',
            report_year=year,
            report_month__icontains=month
        ).values('organization__id').annotate(
            criminal_pending_start_of_month=Sum('pending_start_of_month'),
            criminal_instituted_during_the_month=Sum('instituted_during_the_month'),
            criminal_total_count=Sum('total_count'),
            criminal_count_disposed_contested=Sum('count_disposed_contested'),
            criminal_count_disposed_uncontested=Sum('count_disposed_uncontested'),
            criminal_count_disposed_transferred=Sum('count_disposed_transferred'),
            criminal_pending_in_hand=Sum('pending_in_hand'),
            criminal_pending_more_than_2yrs=Sum('pending_more_then_2yrs'),
            criminal_pending_more_than_4yrs=Sum('pending_more_then_4yrs'),
            criminal_unit=Sum('unit'),
            criminal_no_of_working_days=Sum('no_of_working_days')
        )

        # Combine both civil and criminal results

        for civil in civil_main_query:
            org_id = civil['organization__id']
            criminal = next((cr for cr in criminal_main_query if cr['organization__id'] == org_id), {})
            
            combined_data = {
                'organization_id': civil['organization__id'],
                'organization_shortname': civil['organization__organization_shortname'],
                'case_type': 'main',
                **civil,
                **{key: criminal.get(key) for key in criminal if criminal}
            }
            result.append(combined_data)



        # Query for the 'misc' case type with 'criminal' category
        criminal_misc_query = report_models.Report.objects.filter(
            case_type__type_main_mis='misc',
            case_type__type_civil_criminal='criminal',
            report_year=year,
            report_month__icontains=month
        ).values('organization__id').annotate(
            criminal_pending_start_of_month=Sum('pending_start_of_month'),
            criminal_instituted_during_the_month=Sum('instituted_during_the_month'),
            criminal_total_count=Sum('total_count'),
            criminal_count_disposed_contested=Sum('count_disposed_contested'),
            criminal_count_disposed_uncontested=Sum('count_disposed_uncontested'),
            criminal_count_disposed_transferred=Sum('count_disposed_transferred'),
            criminal_pending_in_hand=Sum('pending_in_hand'),
            criminal_pending_more_than_2yrs=Sum('pending_more_then_2yrs'),
            criminal_pending_more_than_4yrs=Sum('pending_more_then_4yrs'),
            criminal_unit=Sum('unit'),
            criminal_no_of_working_days=Sum('no_of_working_days')
        )

        # Combine both civil and criminal results

        for civil in civil_misc_query:
            org_id = civil['organization__id']
            criminal = next((cr for cr in criminal_misc_query if cr['organization__id'] == org_id), {})
            
            combined_data = {
                'organization_id': civil['organization__id'],
                'organization_shortname': civil['organization__organization_shortname'],
                'case_type': 'misc',
                **civil,
                **{key: criminal.get(key) for key in criminal if criminal}
            }
            result.append(combined_data)


        
       
        # Query for 'main' case types similarly for both civil and criminal
        # Repeat the same process for 'main' case type similar to 'misc'
        # Add the results in 'result' list

        # Return the response
        return response.Response(result)
    
class MonthlyCaseStatementReport(views.APIView):

    """
    API to fetch data from the organization-specific database.
    """
    def get(self, request, *args, **kwargs):

        try:
            query_params = self.request.query_params
            serializer = report_serializer.CaseStatementReportQueryParameterSerializer(data=query_params)
            if serializer.is_valid():
                validated_data = serializer.validated_data

            # Dynamically fetch the database connection for the org_id
                
                org_id=utility.get_organization_id(self.request)
                connection=utility.DatabaseConnectionManager.get_connection(org_id)
                
                present_month_start_date_string =str(validated_data['year']) + '-' + str(validated_data['month'])+'-01'
                present_month_start_date_obj = datetime.strptime(present_month_start_date_string, '%Y-%m-%d')
                prev_month_end_date_obj = present_month_start_date_obj - timedelta(days=1)
                # Get the last day of the month
                present_month_last_day = calendar.monthrange(present_month_start_date_obj.year, present_month_start_date_obj.month)[1]

                # Calculate the end date of the month
                present_month_end_date_obj = present_month_start_date_obj.replace(day=present_month_last_day)
                
                present_month_start_date ="'" + present_month_start_date_string + "'"
                last_month_end_date = "'" + str(prev_month_end_date_obj) + "'"
                present_month_end_date = "'"+str(present_month_end_date_obj)+"'"
                criminal_civil_flag ="'"+ str(validated_data['criminal_civil_flag'])+"'"

                sql_query= '''
                        SELECT      COALESCE(ins_pen.case_type, con.case_type) AS case_type,
                                    COALESCE(ins_pen.type_name, con.type_name) AS type_name,
                                    COALESCE(ins_pen.pen_casecount,0) AS pen_casecount,
                                    COALESCE(ins_pen.ins_casecount,0) AS ins_casecount,
                                    COALESCE(con.contested_count,'0') AS contested_count,
                                    COALESCE(uncon.uncontested_count,'0') AS uncontested_count,
                                    COALESCE(tran.transfer_count, '0') AS transfer_count,
                                    COALESCE(month_end_pend.end_pending_count,'0') AS month_end_count,
                                    month_end_pend.oldestdate,
                                    COALESCE(four_month_old.four_month_old_count, '0') AS four_month_old_count,
                                    COALESCE(two_years_old.two_years_old_count, '0') AS two_years_old_count
                            FROM (
                                
                                    SELECT  COALESCE(ins.case_type,pen.case_type) AS case_type, 
                                            COALESCE(ins.type_name,pen.type_name) AS type_name, 
                                            COALESCE(pen.casecount,'0') AS pen_casecount,
                                            COALESCE(ins.casecount, '0') AS ins_casecount 
                                    FROM    
                                        (

                                            SELECT  a.case_type,  
                                                    a.type_name, 
                                                    COALESCE(COUNT(b.regcase_type),'0') AS casecount 
                                            FROM public.case_type_t AS a 
                                            LEFT JOIN 
                                            (
                                                SELECT * FROM civil_t WHERE  dt_regis <= ''' + last_month_end_date+ ''' 
                                                UNION 
                                                SELECT * FROM civil_t_a WHERE dt_regis <= ''' + last_month_end_date+ '''  AND  date_of_decision > ''' + last_month_end_date+ ''' 
                                            )  as b ON b.regcase_type = a.case_type   
                                            WHERE a.type_flag = ''' + criminal_civil_flag+ '''  AND a.display='Y'
                                            GROUP BY a.case_type, a.type_name 
                                            ORDER BY a.case_type
                                            
                                        ) AS pen 
                                        FULL OUTER JOIN
                                
                                        (
                                            SELECT  a.case_type, 
                                                    a.type_name, 
                                                    COALESCE( COUNT(b.regcase_type),0) AS casecount 
                                            FROM case_type_t AS a 
                                            LEFT JOIN  
                                            (
                                            SELECT * FROM civil_t 
                                                    WHERE  dt_regis >= ''' + present_month_start_date+ '''  AND dt_regis <= ''' + present_month_end_date+ ''' 
                                                    UNION 
                                            SELECT * FROM civil_t_a 
                                                    WHERE dt_regis >= ''' + present_month_start_date+ '''  AND dt_regis <= ''' + present_month_end_date+ ''' 
                                            ) AS b ON b.regcase_type = a.case_type   
                                            WHERE a.type_flag = ''' + criminal_civil_flag+ '''AND a.display='Y'
                                            GROUP BY a.case_type, a.type_name ORDER BY a.case_type
                                        ) AS ins on ins.case_type=pen.case_type ---ORDER BY casecount desc
                                ) AS ins_pen
                                
                                FULL OUTER JOIN
                                (
                                    SELECT  a.case_type, 
                                            a.type_name ,
                                            CASE WHEN b.regcase_type IS NULL THEN 0 ELSE   COUNT(*) END AS contested_count 
                                    FROM case_type_t AS a 
                                    LEFT OUTER JOIN  
                                    ( 
                                        SELECT * 
                                        FROM civil_t_a 
                                        WHERE  (date_of_decision  >=  ''' + present_month_start_date+ '''  AND date_of_decision <= ''' + present_month_end_date+ '''  ) AND goshwara_no = 1
                                    ) AS b ON b.regcase_type = a.case_type 
                                    WHERE a.type_flag = ''' + criminal_civil_flag+ ''' AND a.display='Y'  
                                    GROUP BY a.type_name , a.case_type , b.regcase_type
                                ) AS con ON con.case_type = ins_pen.case_type
                                
                                FULL OUTER JOIN
                                
                                (
                                    SELECT  a.case_type, 
                                            type_name ,
                                            CASE WHEN regcase_type IS NULL THEN 0 ELSE   COUNT(*) END AS uncontested_count 
                                    FROM case_type_t AS a 
                                    LEFT OUTER JOIN  
                                    ( 
                                    SELECT
                                    * 
                                    FROM civil_t_a 
                                    WHERE  (date_of_decision  >= ''' + present_month_start_date+ '''  AND date_of_decision <= ''' + present_month_end_date+ '''  ) 
                                            AND 
                                            goshwara_no = 2
                                    ) AS b ON b.regcase_type = a.case_type 
                                    WHERE a.type_flag =''' + criminal_civil_flag+ ''' AND a.display='Y'  
                                    GROUP BY a.type_name , a.case_type , b.regcase_type
                                ) AS uncon ON uncon.case_type = ins_pen.case_type
                                
                                FULL OUTER JOIN
                                (
                                    SELECT  a.case_type , 
                                            type_name ,
                                            CASE WHEN b.regcase_type IS NULL THEN 0 ELSE   COUNT(*) END AS transfer_count 
                                            FROM case_type_t AS a 
                                    LEFT OUTER JOIN  
                                    ( 
                                    SELECT
                                    * 
                                    FROM civil_t_a 
                                    WHERE  (date_of_decision  >= ''' + present_month_start_date+ '''  AND date_of_decision <= ''' + present_month_end_date+ '''  ) AND transfer_est = 'Y'
                                    ) AS b ON b.regcase_type = a.case_type 
                                    WHERE a.type_flag = ''' + criminal_civil_flag+ ''' AND a.display='Y' 
                                    GROUP BY a.type_name ,a.case_type , b.regcase_type
                                ) AS tran ON tran.case_type = ins_pen.case_type
                                
                                FULL OUTER JOIN 
                                (
                                    SELECT  a.type_name, 
                                            a.case_type , 
                                            CASE WHEN b.regcase_type  IS NULL THEN 0 ELSE  COUNT(b.regcase_type) END AS end_pending_count ,  
                                            min(dt_regis) AS oldestdate
                                    FROM case_type_t AS a
                                    LEFT OUTER JOIN  
                                    (

                                    SELECT 
                                        * 
                                    FROM civil_t 
                                    WHERE  dt_regis <= ''' + present_month_end_date+ ''' 
                                    UNION 
                                    SELECT 
                                        * 
                                    FROM civil_t_a 
                                    WHERE dt_regis <= ''' + present_month_end_date+ '''  AND  date_of_decision > ''' + present_month_end_date+ ''' 

                                    ) AS b  ON b.regcase_type = a.case_type 
                                    WHERE a.type_flag = ''' + criminal_civil_flag+ ''' AND a.display='Y' 
                                    GROUP BY a.type_name,a.case_type, b.regcase_type
                                
                                ) AS month_end_pend ON month_end_pend.case_type = ins_pen.case_type
                                
                                FULL OUTER JOIN
                                
                                (
                                    SELECT  a.case_type , 
                                            type_name , 
                                            CASE WHEN  b.regcase_type IS NULL THEN 0 ELSE  COUNT(*) END AS four_month_old_count 
                                            FROM case_type_t a 
                                    LEFT OUTER JOIN  
                                    ( 
                                        SELECT 
                                            * 
                                        FROM civil_t
                                        WHERE  dt_regis <= ''' + present_month_end_date+ '''  AND dt_regis <= ( ''' + present_month_end_date+ ''' ::DATE - INTERVAL '4 MONTHS')  
                                            UNION 
                                        SELECT  
                                            * 
                                        FROM civil_t_a 
                                        WHERE dt_regis <= ''' + present_month_end_date+ '''  AND  date_of_decision > ''' + present_month_end_date+ '''  AND dt_regis <= ( ''' + present_month_end_date+ ''' ::DATE - INTERVAL '4 MONTHS')
                                    )   AS b ON b.regcase_type = a.case_type 
                                    WHERE a.type_flag = ''' + criminal_civil_flag+ ''' AND a.display='Y'  
                                    GROUP BY a.type_name ,  a.case_type ,  b.regcase_type
                                ) AS four_month_old  ON four_month_old.case_type = ins_pen.case_type
                                
                                FULL OUTER JOIN
                                (
                                    SELECT  a.case_type , 
                                            type_name , 
                                            CASE WHEN  b.regcase_type IS NULL THEN 0 ELSE  COUNT(*) END AS two_years_old_count 
                                    FROM case_type_t AS a 
                                    LEFT OUTER JOIN  
                                    ( 
                                        SELECT 
                                            * 
                                        FROM civil_t 
                                        WHERE  dt_regis <= ''' + present_month_end_date+ '''  AND dt_regis <= ( ''' + present_month_end_date+ ''' ::DATE - INTERVAL '2 YEARS')  
                                            UNION 
                                        SELECT 
                                            * 
                                        FROM civil_t_a 
                                        WHERE dt_regis <= ''' + present_month_end_date+ '''  AND  date_of_decision > ''' + present_month_end_date+ '''  AND dt_regis <= ( ''' + present_month_end_date+ ''' ::DATE - INTERVAL '2 YEARS')
                                    ) AS b on b.regcase_type = a.case_type 
                                    WHERE a.type_flag = ''' + criminal_civil_flag+ ''' AND a.display='Y'
                                    GROUP BY a.type_name ,  a.case_type , b.regcase_type
                                ) AS  two_years_old on two_years_old.case_type = ins_pen.case_type;
                                '''
                print('SQL Query', sql_query)
                with connection.cursor() as cursor:
                    cursor.execute(
                       
                            sql_query
                        
                    )
                    rows = cursor.fetchall()
                    data = [
                        {
                        "case_type": row[0], 
                        "type_name": row[1], 
                        "pen_casecount": row[2], 
                        "ins_casecount": row[3],
                        "contested_count": row[4],
                        "uncontested_count": row[5],
                        "transfer_count": row[6],
                        "month_end_count": row[7],
                        "oldestdate": row[8],
                        "four_month_old_count": row[9],
                        "two_years_old_count": row[10],
                         
                         }
                        for row in rows
                    ]

                    # utility.DatabaseConnectionManager.release_connection(org_id, connection)
                    # utility.DatabaseConnectionManager.close_all_connections()
                    return response.Response({"data": data})
            else :
                errors = serializer.errors
                # logger.error(f"Validation errors: {errors}")
                return response.Response({"error": errors}, status=400)
                # return exceptions.APIException(detail='Required Query Parameters are not valid!')
            
        except ValueError as ve:
            # del connections.databases[connection_name]
            return response.Response({"error": str(ve)}, status=400)
        except Exception as e:
            print('Custom Error:', e)
            # del connections.databases[connection_name]
            return response.Response({"error": str(e)}, status=500)
        


def get_case_type(request, validated_data):
    try:
       
        org_id=utility.get_organization_id(request)
       
        connection=utility.DatabaseConnectionManager.get_connection(org_id)
        
        present_month_start_date_string =str(validated_data['year']) + '-' + str(validated_data['month'])+'-01'
        present_month_start_date_obj = datetime.strptime(present_month_start_date_string, '%Y-%m-%d')
        prev_month_end_date_obj = present_month_start_date_obj - timedelta(days=1)
        # Get the last day of the month
        present_month_last_day = calendar.monthrange(present_month_start_date_obj.year, present_month_start_date_obj.month)[1]

        # Calculate the end date of the month
        present_month_end_date_obj = present_month_start_date_obj.replace(day=present_month_last_day)
        
        present_month_start_date ="'" + present_month_start_date_string + "'"
        last_month_end_date = "'" + str(prev_month_end_date_obj) + "'"
        present_month_end_date = "'"+str(present_month_end_date_obj)+"'"
        criminal_civil_flag = "'"+ str(validated_data['criminal_civil_flag'])+"'"

        # case_type =  "'"+ str(case_type)+"'"

        sql_query=  '''
                SELECT DISTINCT * FROM (
                SELECT 
                    a.case_type, 
                    a.type_name

                FROM case_type_t a 
                    JOIN  
                ( 
                        SELECT cta.regcase_type  FROM civil_t_a as cta
                        join
                        public.disp_type_t as dtt on cta.disp_nature = dtt.disp_type
                        WHERE date_of_decision  >=  ''' + present_month_start_date + ''' AND date_of_decision <= ''' + present_month_end_date + '''
                ) as b on b.regcase_type = a.case_type 
                WHERE a.type_flag = ''' + criminal_civil_flag + ''' AND a.display='Y'
                ) as ct    '''
       
        data = []
        with connection.cursor() as cursor:
            cursor.execute(
                
                    sql_query
                
            )
            rows = cursor.fetchall()
            data = [
                {
                "case_type": row[0], 
                "type_name": row[1],
               
            
                }
                for row in rows
            ]
        utility.DatabaseConnectionManager.release_connection(org_id, connection)
        return data
    except ValueError as ve:
            # del connections.databases[connection_name]
            return response.Response({"error": str(ve)}, status=400)
    except Exception as e:
        print('Custom Error:', e)
        # del connections.databases[connection_name]
        return response.Response({"error": str(e)}, status=500)
    # finally:
    #     utility.DatabaseConnectionManager.close_all_connections()



class MonthlyDisposedTransferredReport(views.APIView):

    """
    API to fetch data from the organization-specific database.
    """
    def get(self, request, *args, **kwargs):

        try:
            query_params = self.request.query_params
            serializer = report_serializer.CaseStatementReportQueryParameterSerializer(data=query_params)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                case_type_data = get_case_type(self.request, validated_data)
               
                final_data = []
                if case_type_data:
                    
                    for row in case_type_data:
                       
                        data = self.get_disposed_transfered_case(self.request, validated_data,row['case_type'])
                        # print('case_type:', row['case_type'])
                        # print('Result:',data)

                        final_data.append(
                            {
                                'case_type' : row['case_type'],
                                'type_name' : row['type_name'],
                                'data' : data
                            }
                        )
                return response.Response({"data": final_data})
            else :
                errors = serializer.errors
                # logger.error(f"Validation errors: {errors}")
                return response.Response({"error": errors}, status=400)
                # return exceptions.APIException(detail='Required Query Parameters are not valid!')
            
        except ValueError as ve:
            # del connections.databases[connection_name]
            return response.Response({"error": str(ve)}, status=400)
        except Exception as e:
            print('Custom Error:', e)
            # del connections.databases[connection_name]
            return response.Response({"error": str(e)}, status=500)
        
    def get_disposed_transfered_case(self,request, validated_data, case_type):
        try:
            org_id=utility.get_organization_id(request)

            connection=utility.DatabaseConnectionManager.get_connection(org_id)
            
            present_month_start_date_string =str(validated_data['year']) + '-' + str(validated_data['month'])+'-01'
            present_month_start_date_obj = datetime.strptime(present_month_start_date_string, '%Y-%m-%d')
            prev_month_end_date_obj = present_month_start_date_obj - timedelta(days=1)
            # Get the last day of the month
            present_month_last_day = calendar.monthrange(present_month_start_date_obj.year, present_month_start_date_obj.month)[1]

            # Calculate the end date of the month
            present_month_end_date_obj = present_month_start_date_obj.replace(day=present_month_last_day)
            
            present_month_start_date ="'" + present_month_start_date_string + "'"
            last_month_end_date = "'" + str(prev_month_end_date_obj) + "'"
            present_month_end_date = "'"+str(present_month_end_date_obj)+"'"
            criminal_civil_flag = "'"+ str(validated_data['criminal_civil_flag'])+"'"

            case_type =  "'"+ str(case_type)+"'"

            sql_query=  '''
                    SELECT 
                        a.case_type, 
                        a.type_name, 
                        b.pet_name, 
                        b.res_name, 
                        b.reg_no, 
                        b.reg_year, 
                        b.goshwara_no, 
                        b.disp_nature,
                        b.disp_name, 
                        b.date_of_decision,
                        b.transfer_est

                    FROM case_type_t a 
                        JOIN  
                    ( 
                            SELECT cta.* , dtt.disp_name  FROM civil_t_a as cta
                            join
                            public.disp_type_t as dtt on cta.disp_nature = dtt.disp_type
                            WHERE date_of_decision  >=  ''' + present_month_start_date + ''' AND date_of_decision <= ''' + present_month_end_date + '''
                    ) as b on b.regcase_type = a.case_type 
                    WHERE a.type_flag = ''' + criminal_civil_flag + ''' AND a.display='Y' AND a.case_type = ''' + case_type + ''' 
                        '''
        
            data=[]
            with connection.cursor() as cursor:
                cursor.execute(
                    
                        sql_query
                    
                )
                rows = cursor.fetchall()
                data = [
                    {
                    "case_type": row[0], 
                    "type_name": row[1], 
                    "pet_name": row[2], 
                    "res_name": row[3],
                    "goshwara_no": row[4],
                    "reg_year": row[5],
                    "disp_nature": row[6],
                    "disp_name": row[7],
                    "date_of_decision": row[8],
                    "transfer_est": row[9],
                
                        }
                    for row in rows
                ]
            utility.DatabaseConnectionManager.release_connection(org_id, connection)
            return data
        
        except ValueError as ve:
                # del connections.databases[connection_name]
                return response.Response({"error": str(ve)}, status=400)
        except Exception as e:
            print('Custom Error:', e)
            # del connections.databases[connection_name]
            return response.Response({"error": str(e)}, status=500)
        # finally:
        #     utility.DatabaseConnectionManager.close_all_connections()
        


class MonthEndPendingCasesReport(views.APIView):

    """
    API to fetch data from the organization-specific database.
    """
    def get(self, request, *args, **kwargs):

        try:
            query_params = self.request.query_params
            serializer = report_serializer.CaseStatementReportQueryParameterSerializer(data=query_params)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                case_type_data = get_case_type(self.request, validated_data)
               
                final_data = []
                if case_type_data:
                    
                    for row in case_type_data:
                       
                        data = self.get_pending_case(self.request, validated_data,row['case_type'])
                        # print('case_type:', row['case_type'])
                        # print('Result:',data)

                        final_data.append(
                            {
                                'case_type' : row['case_type'],
                                'type_name' : row['type_name'],
                                'data' : data
                            }
                        )
                return response.Response({"data": final_data})
            else :
                errors = serializer.errors
                # logger.error(f"Validation errors: {errors}")
                return response.Response({"error": errors}, status=400)
                # return exceptions.APIException(detail='Required Query Parameters are not valid!')
            
        except ValueError as ve:
            # del connections.databases[connection_name]
            return response.Response({"error": str(ve)}, status=400)
        except Exception as e:
            print('Custom Error:', e)
            # del connections.databases[connection_name]
            return response.Response({"error": str(e)}, status=500)
        
    def  get_pending_case(self, request, validated_data,case_type):

        try:
            org_id=utility.get_organization_id(request)

            connection=utility.DatabaseConnectionManager.get_connection(org_id)
            
            present_month_start_date_string =str(validated_data['year']) + '-' + str(validated_data['month'])+'-01'
            present_month_start_date_obj = datetime.strptime(present_month_start_date_string, '%Y-%m-%d')
            prev_month_end_date_obj = present_month_start_date_obj - timedelta(days=1)
            # Get the last day of the month
            present_month_last_day = calendar.monthrange(present_month_start_date_obj.year, present_month_start_date_obj.month)[1]

            # Calculate the end date of the month
            present_month_end_date_obj = present_month_start_date_obj.replace(day=present_month_last_day)
            
            present_month_start_date ="'" + present_month_start_date_string + "'"
            last_month_end_date = "'" + str(prev_month_end_date_obj) + "'"
            present_month_end_date = "'"+str(present_month_end_date_obj)+"'"
            criminal_civil_flag = "'"+ str(validated_data['criminal_civil_flag'])+"'"

            case_type =  "'"+ str(case_type)+"'"

            sql_query=  '''
                    SELECT 
                          
                            a.case_type, 
                            a.type_name, 
                            b.pet_name, 
                            b.res_name, 
                            b.cino, 
                            pet.respondents AS ext_respondents, 
                            b.dt_regis, 
                            b.reg_no, 
                            b.reg_year, 
                            s.relief_offense,
                            act.act_section
                      
                        FROM case_type_t a
                        JOIN (
                            SELECT * 
                            FROM civil_t 
                            WHERE dt_regis <= '''+ last_month_end_date +'''
                            UNION 
                            SELECT * 
                            FROM civil_t_a 
                            WHERE dt_regis <= '''+ last_month_end_date +''' AND date_of_decision > '''+ last_month_end_date +''' 
                        ) AS b 
                        ON b.regcase_type = a.case_type 
                        LEFT JOIN (
                            SELECT 
                                cino,
                                JSON_AGG(
                                    JSON_BUILD_OBJECT('sl_no', row_number, 'respondent', pet_name)
                                ) AS respondents
                            FROM (
                                SELECT 
                                    cino, 
                                    pet_name, 
                                    ROW_NUMBER() OVER (PARTITION BY cino ORDER BY pet_name) AS row_number
                                FROM (
                                    SELECT 
                                        cino, 
                                        name AS pet_name  
                                    FROM civ_address_t 
                                    UNION
                                    SELECT 
                                        cino, 
                                        name AS pet_name   
                                    FROM civ_address_t_a 
                                ) AS d
                            ) AS r
                            GROUP BY cino
                        ) AS pet 
                        ON pet.cino = b.cino
                        LEFT JOIN (
                            SELECT 
                                cino, 
                                relief_offense 
                            FROM public.case_info
                            UNION
                            SELECT 
                                cino, 
                                relief_offense 
                            FROM public.case_info_a
                        ) AS s 
                        ON s.cino = b.cino
                        LEFT JOIN (
                            SELECT  
                                cino,
                                    JSON_AGG(
                                        JSON_BUILD_OBJECT('sl_no', sl_no, 'act_section', 'Section ' || section ||' '|| actname)
                                    ) AS act_section
                            
                            FROM (
                            SELECT 
                                    ea.section,
                                    ea.cino, 
                                    a.actname,
                                    ROW_NUMBER() OVER(PARTITION BY ea.cino ORDER BY a.actname) as sl_no
                                FROM public.extraact_t AS ea
                                JOIN public.act_t AS a 
                                ON a.actcode = ea.acts
                                WHERE ea.display = 'Y' --order by sl_no
                                ) as f
                                GROUP BY f.cino
                        ) AS act 
                        ON act.cino = b.cino 
                    WHERE a.type_flag = ''' + criminal_civil_flag + ''' AND a.display='Y' AND a.case_type = ''' + case_type + ''' 
                        '''
        
            data=[]
            with connection.cursor() as cursor:
                cursor.execute(
                    
                        sql_query
                    
                )
                rows = cursor.fetchall()
                data = [
                    {
                    "case_type": row[0], 
                    "type_name": row[1], 
                    "pet_name": row[2], 
                    "res_name": row[3],
                    "cino": row[4],
                    "ext_respondents": row[5],
                    "dt_regis": row[6],
                    "reg_no": row[7],
                    "reg_year": row[8],
                    "relief_offense": row[9],
                    "act_section": row[10],
                   
                        }
                    for row in rows
                ]
            utility.DatabaseConnectionManager.release_connection(org_id, connection)
            return data
        
        except ValueError as ve:
                # del connections.databases[connection_name]
                return response.Response({"error": str(ve)}, status=400)
        except Exception as e:
            print('Custom Error:', e)
            # del connections.databases[connection_name]
            return response.Response({"error": str(e)}, status=500)
        # finally:
        #     utility.DatabaseConnectionManager.close_all_connections()



class MonthlyFeeCollectionReport(views.APIView):

    """
    API to fetch data from the organization-specific database.
    """
    def get(self, request, *args, **kwargs):

        try:
            query_params = self.request.query_params
            serializer = report_serializer.MonthlyFeeCollectionReportQueryParameterSerializer(data=query_params)
            if serializer.is_valid():
                validated_data = serializer.validated_data

            # Dynamically fetch the database connection for the org_id
                
                org_id=utility.get_organization_id(self.request)
                connection=utility.DatabaseConnectionManager.get_connection(org_id)
                
                present_month_start_date_string =str(validated_data['year']) + '-' + str(validated_data['month'])+'-01'
                present_month_start_date_obj = datetime.strptime(present_month_start_date_string, '%Y-%m-%d')
                prev_month_end_date_obj = present_month_start_date_obj - timedelta(days=1)
                # Get the last day of the month
                present_month_last_day = calendar.monthrange(present_month_start_date_obj.year, present_month_start_date_obj.month)[1]

                # Calculate the end date of the month
                present_month_end_date_obj = present_month_start_date_obj.replace(day=present_month_last_day)
                
                present_month_start_date ="'" + present_month_start_date_string + "'"
                last_month_end_date = "'" + str(prev_month_end_date_obj) + "'"
                present_month_end_date = "'"+str(present_month_end_date_obj)+"'"
              

                sql_query=  '''
                        
                            SELECT 
                                c.type_name, --0
                                c.case_type, --1
                                c.pet_name, --2
                                c.res_name, --3
                                c.cino, --4
                                c.dt_regis, --5
                                c.reg_no, --6
                                c.reg_year, --7
                                c.pet_age,--8
                                c.res_age,--9
                                CASE WHEN f.fees_type =1 THEN f.amount 
                                        ELSE 0 
                                    END AS  court_fees, --10
                                    CASE WHEN f.fees_type <> 1 THEN (f.amount + f.aff_fee +
                                    f.vak_fee +
                                    f.other )
                                        ELSE 0 
                                    END AS  other_fees, --11
                                    f.document_type, --12
                                    f.todays_date, --13
                                    f.display, --14
                                    f.filing, --15
                                    f.type, --16
                                    f.bank_code,--17
                                    f.paymode, --18
                                    f.dd_num, --19
                                    f.dd_date, --20
                                    f.receipt_no, --21
                                    f.casenotype, --22
                                    f.receipt_status--23

                            -- CASE WHEN b.regcase_type IS NULL THEN 0 ELSE COUNT(b.regcase_type) END AS end_pending_count,
                            -- MIN(dt_regis) AS oldestdate
                            FROM public.efees_t as f
                            left join (
                                SELECT 
                                a.type_name, 
                                a.case_type, 
                                b.pet_name, 
                                b.res_name, 
                                b.cino, 
                            
                                b.dt_regis, 
                                b.reg_no, 
                                b.reg_year, 
                            
                                b.pet_age,
                                b.res_age

                            -- CASE WHEN b.regcase_type IS NULL THEN 0 ELSE COUNT(b.regcase_type) END AS end_pending_count,
                            -- MIN(dt_regis) AS oldestdate
                            FROM case_type_t a
                            JOIN (
                                SELECT 
                                regcase_type,
                                pet_name, 
                                res_name, 
                                cino, 

                                dt_regis, 
                                reg_no, 
                                reg_year, 
                                pet_age,
                                res_age
                                FROM civil_t 
                                UNION 
                                SELECT 
                                regcase_type,
                                pet_name, 
                                res_name, 
                                cino, 

                                dt_regis, 
                                reg_no, 
                                reg_year, 
                                pet_age,
                                res_age
                                FROM civil_t_a 
                            ) AS b 
                            ON  a.case_type = b.regcase_type 
                            ) as c on c.cino=f.cino
                            WHERE f.todays_date >= ''' + present_month_start_date+ '''  AND f.todays_date <=  ''' + present_month_end_date+ ''' 
                            --========



                            ;
                            '''
                print('SQL Query', sql_query)
                with connection.cursor() as cursor:
                    cursor.execute(
                       
                            sql_query
                        
                    )
                    rows = cursor.fetchall()
                    data = [
                        {
                        "type_name": row[0], 
                        "case_type": row[1], 
                        "pet_name": row[2], 
                        "res_name": row[3],
                        "cino": row[4],
                        "dt_regis": row[5],
                        "reg_no": row[6],
                        "reg_year": row[7],
                        "pet_age": row[8],
                        "res_age": row[9],
                        "court_fees": row[10],
                        "other_fees": row[11],

                        "document_type": row[12],
                        "record_date": row[13],
                        "filing": row[15],
                        "type": row[16],
                        "bank_code": row[17],
                        "paymode": row[18],
                        "dd_num": row[19],
                        "dd_date": row[20],
                        "receipt_no": row[21],
                        "casenotype": row[22],
                        "receipt_status": row[23],


                         
                         }
                        for row in rows
                    ]
                
                    # utility.DatabaseConnectionManager.release_connection(org_id, connection)
                    # utility.DatabaseConnectionManager.close_all_connections()
                    return response.Response({"data": data})
            else :
                errors = serializer.errors
                # logger.error(f"Validation errors: {errors}")
                return response.Response({"error": errors}, status=400)
                # return exceptions.APIException(detail='Required Query Parameters are not valid!')
            
        except ValueError as ve:
            # del connections.databases[connection_name]
            return response.Response({"error": str(ve)}, status=400)
        except Exception as e:
            print('Custom Error:', e)
            # del connections.databases[connection_name]
            return response.Response({"error": str(e)}, status=500)
        

class MonthEndUnderTrialPrisonerReport(views.APIView):

    """
    API to fetch data from the organization-specific database.
    """
    def get(self, request, *args, **kwargs):

        try:
            
            
            # Dynamically fetch the database connection for the org_id
                
            org_id=utility.get_organization_id(self.request)
            connection=utility.DatabaseConnectionManager.get_connection(org_id)
            

            sql_query=  '''
                    
                           SELECT 
                            c.type_name, --0
                            c.case_type, --1
                            c.pet_name, --2
                            c.res_name, --3
                            c.cino, --4
                        
                            c.dt_regis,--5 
                            c.reg_no, --6
                            c.reg_year, --7
                        
                            c.pet_age,--8
                            c.res_age,--9

                            lpet_res, --10
                            arrest_date, --11
                            bail_date, --12
                            custody_type, --13
                            name1, --14
                            lname1, --15
                            amount1, --16
                            property1, --17
                            lproperty1, --18
                            name2, --19
                            lname2, --20
                            amount2, --21
                            property2, --22
                            lproperty2, --23
                            remarks, --24
                            prison_id, --25
                            landphone1, --26
                            landphone2, --27
                            age1, --28
                            age2, --29
                            mobile1, --30
                            mobile2, --31
                            address1, --32
                            address2, --33
                            street1, --34
                            street2,--35
                            pincode1, --36
                            pincode2, --37
                            dist_code1, --38
                            dist_code2,--39
                            taluka_code1, --40
                            taluka_code2, --41
                            hobli1, --42
                            hobli2, --43
                            hamlet1, --44
                            hamlet2,--45
                            village_code1,--46 
                            village_code2, --47
                            town_code1, --48
                            town_code2,--49
                            ward_code1, --50
                            ward_code2, --51
                            father_name1, --52
                            father_name2, --53
                            org_name1, --54
                            org_name2, --55
                            uid1, uid2, --56
                            release_date, --57
                            ut.cino, --58
                            srno, --59
                            max_act_national_code, --60 
                            max_section, --61
                            max_imprisonment,--62 
                            life_death, 63
                            state_id1, --64
                            state_id2, --65
                            amd, --66
                            create_modify,--67 
                            e_prisonerid, --68
                            party_no, --69
                            type --70
                           
                            FROM public.under_trial as ut

                            left join (
                                    SELECT 
                                    a.type_name, 
                                    a.case_type, 
                                    b.pet_name, 
                                    b.res_name, 
                                    b.cino, 
                                
                                    b.dt_regis, 
                                    b.reg_no, 
                                    b.reg_year, 
                                
                                    b.pet_age,
                                    b.res_age

                                -- CASE WHEN b.regcase_type IS NULL THEN 0 ELSE COUNT(b.regcase_type) END AS end_pending_count,
                                -- MIN(dt_regis) AS oldestdate
                                FROM case_type_t a
                                JOIN (
                                    SELECT 
                                    regcase_type,
                                    pet_name, 
                                    res_name, 
                                    cino, 

                                    dt_regis, 
                                    reg_no, 
                                    reg_year, 
                                    pet_age,
                                    res_age
                                    FROM civil_t 
                                    UNION 
                                    SELECT 
                                    regcase_type,
                                    pet_name, 
                                    res_name, 
                                    cino, 

                                    dt_regis, 
                                    reg_no, 
                                    reg_year, 
                                    pet_age,
                                    res_age
                                    FROM civil_t_a 
                                ) AS b 
                                ON  a.case_type = b.regcase_type 
                            ) as c on c.cino=ut.cino
                        ;

                        
                        '''
            print('SQL Query', sql_query)
            with connection.cursor() as cursor:
                    cursor.execute(
                       
                            sql_query
                        
                    )
                    rows = cursor.fetchall()
                    data = [
                        {
                        "type_name": row[0], 
                        "case_type": row[1], 
                        "pet_name": row[2], 
                        "res_name": row[3],
                        "cino": row[4],
                        "dt_regis": row[5],
                        "reg_no": row[6],
                        "reg_year": row[7],
                        "pet_age": row[8],
                        "res_age": row[9],
                        "arrest_date":row[11],
                         
                         }
                        for row in rows
                    ]

                    # utility.DatabaseConnectionManager.release_connection(org_id, connection)
                    # utility.DatabaseConnectionManager.close_all_connections()
                    return response.Response({"data": data})
            
        except ValueError as ve:
            # del connections.databases[connection_name]
            return response.Response({"error": str(ve)}, status=400)
        except Exception as e:
            print('Custom Error:', e)
            # del connections.databases[connection_name]
            return response.Response({"error": str(e)}, status=500)
        



