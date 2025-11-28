from django.urls import path
# from .views import AuditLogListView

from . import views


urlpatterns = [
    path('summary/', views.ReportSummaryView.as_view(), name='get_summary_reports'),
    path('report/', views.ListCreateReportAPIView.as_view(), name='get_post_reports'),
    path('notesheet/', views.ReportNoteSheetApiView.as_view(), name='get_notesheet_reports'),

    path('with/case_type', views.ListCreateReportAPIView.as_view(), name='get_post_reports'),
    path('<int:pk>/', views.RetrieveUpdateDestroyReportAPIView.as_view(), name='get_delete_update_report'),
    path('audit-logs/',views.AuditLogListView.as_view(), name='audit-log-list'),
    path('report/oldest_case/<int:pk>', views.OldestCaseDetails.as_view(), name='oldest_case'),
    path('report/oldest_case/get', views.OldestCaseDetailsRetrieve.as_view(), name='oldest_case_retrieve'),
    path('report/case_type/',views.CaseTypeList.as_view()),

    path('report/disposed/cases/', views.DisposedCaseReportList.as_view() ),
    path('report/disposed/cases/get/for/hcs', views.DisposedCaseReportListGetForHCS.as_view() ),

    path('report/pending/cases/', views.PendingCasesReportList.as_view() ),
    path('report/pending/cases/get/for/hcs', views.PendingCasesReportListGetForHCS.as_view() ),

    path('report/pending/cases/above/sixty/', views.PendingCasesPartiesAboveSixtyList.as_view() ),
    path('report/pending/cases/above/sixty/get/for/hcs', views.PendingCasesPartiesAboveSixtyListGetForHCS.as_view() ),

    path('report/court/fee/', views.SatementOfCourtFeeFineList.as_view() ),
    path('report/court/fee/get/for/hcs', views.StatementOfCourtFeesFinesListGetForHCS.as_view() ),

    path('report/long/pending/cases/', views.LongPendingCasesReportList.as_view() ),
    path('report/long/pending/cases/get/for/hcs', views.LongPendingCasesReportListGetForHCS.as_view() ),

    path('report/under/trial/prisoners/', views.ListOfUndertrialPrisonersList.as_view() ),
    path('report/under/trial/prisoners/get/for/hcs', views.ListOfUndertrialPrisonersListGetForHCS.as_view() ),

    path('report/ex-parte/injunction/', views.ExParteInjunctionCasesReportList.as_view() ),
    path('report/ex-parte/injunction/get/for/hcs', views.ExParteInjunctionCasesReportListGetForHCS.as_view() ),

    path('cis/org/database', views.OrganizationDatabaseList.as_view() ),
    path('cis/org/database/<int:pk>', views.OrganizationDatabaseDetails.as_view() ),
    path('cis/report/monthly_case_statement', views.MonthlyCaseStatementReport.as_view() ),
    path('cis/report/disposed_transfered', views.MonthlyDisposedTransferredReport.as_view() ),
    path('cis/report/pending', views.MonthEndPendingCasesReport.as_view() ),
    path('cis/report/fee/monthly/collection', views.MonthlyFeeCollectionReport.as_view() ),
    path('cis/report/present/prisoner', views.MonthEndUnderTrialPrisonerReport.as_view() ),

    

    


]