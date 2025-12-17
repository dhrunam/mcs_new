from django.db import models
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from accounts import models as auth_models

from django.db import models

class OrganizationDatabase(models.Model):
    organisation= models.ForeignKey(auth_models.Organization, null=True, on_delete=models.SET_NULL, related_name='organisation_database') # Organization ID
    db_name = models.CharField(max_length=100)  # Database name
    db_user = models.CharField(max_length=100)  # Database user
    db_password = models.CharField(max_length=100)  # Database password
    db_host = models.CharField(max_length=100, default='localhost')  # Host
    db_port = models.CharField(max_length=10, default='5432')  # Port
    history = AuditlogHistoryField()
    def __str__(self) -> str:
        return f"Organization {self.organisation.organization_name}"

auditlog.register(OrganizationDatabase)

class CaseType(models.Model):
    # organisation= models.ForeignKey(auth_models.Organization, null=True, on_delete=models.SET_NULL, related_name='organisation_casetype') # Organization ID
    desc_case = models.CharField(max_length=600)
    type_main_mis = models.CharField(max_length=15, null=True)
    type_civil_criminal = models.CharField(max_length=15, null=True)
    dist_and_session_judge = models.BooleanField(default=False)
    cjm_cum_civil_judge= models.BooleanField(default=False)
    civil_judge_cum_jm= models.BooleanField(default=False)
    family_court = models.BooleanField(default=False)
    fast_track_court = models.BooleanField(default=False)
    juvenile_justice_court = models.BooleanField(default=False)
    history = AuditlogHistoryField()

    def __str__(self) -> str:
        return self.desc_case
auditlog.register(CaseType)

class OldestCase(models.Model):
    case_type = models.ForeignKey(CaseType,null=True,on_delete=models.SET_NULL, related_name="oldest_case")
    case_no =  models.CharField(max_length=50, null=True)
    petitioner = models.CharField(max_length=1028, null=True)
    responder = models.CharField(max_length=1028, null=True)
    remarks = models.CharField(max_length=1028, null=True)
    date_of_inst = models.DateField(null=True)
    status= models.CharField(max_length=1028, null=True)
    report_year = models.IntegerField()
    report_month=models.CharField(max_length=100)
    organization= models.ForeignKey(auth_models.Organization, on_delete= models.SET_NULL, null=True, related_name='oldest_case')
    created_by = models.ForeignKey('auth.User', related_name='oldest_case_creator', null=True, on_delete=models.SET_NULL)
    updated_by = models.ForeignKey('auth.User', related_name='oldest_case_updator', null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = AuditlogHistoryField()

auditlog.register(OldestCase)

class Report(models.Model):
    id = models.BigAutoField(primary_key=True)
    case_type = models.ForeignKey(CaseType,null=True,on_delete=models.SET_NULL, related_name="report")
    pending_start_of_month=models.IntegerField()
    instituted_during_the_month=models.IntegerField()
    total_count=models.IntegerField()
    count_disposed_contested=models.IntegerField()
    count_disposed_uncontested=models.IntegerField()
    count_disposed_transferred=models.IntegerField()
    pending_in_hand=models.IntegerField()
    pending_more_then_2yrs=models.IntegerField()
    pending_more_then_4yrs=models.IntegerField()
    date_of_oldest_case=models.DateField(null=True)
    unit=models.IntegerField()
    no_of_working_days=models.IntegerField()
    report_year = models.IntegerField()
    report_month=models.CharField(max_length=100, null=True,blank=True)
    remarks=models.CharField(max_length=1500, null=True)
    is_draft=models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    organization= models.ForeignKey(auth_models.Organization, on_delete= models.SET_NULL, null=True, related_name='reports')
    created_by = models.ForeignKey('auth.User', related_name='reports_creator', on_delete=models.CASCADE)
    updated_by = models.ForeignKey('auth.User', related_name='reports_updator', null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['-id']
        unique_together =['case_type','report_year','report_month','organization']

    history = AuditlogHistoryField()
auditlog.register(Report)

class DisposedCasesReport(models.Model):
    case_no =  models.CharField(max_length=50, null=True, blank=True)
    petitioner = models.CharField(max_length=1024, null=True, blank=True)
    responder = models.CharField(max_length=1024, null=True, blank=True)
    case_title = models.CharField(max_length=1024, null=True, blank=True)
    case_type = models.CharField(max_length=1024, null=True, blank=True)
    # case_type = models.ForeignKey(CaseType,null=True,on_delete=models.SET_NULL, related_name="pending_case")
    civil_criminal = models.CharField(max_length=50, null=True, blank=True)
    disposed_transfered = models.CharField(max_length=50, null=True, blank=True)
    goshwara_no =  models.CharField(max_length=50, null=True, blank=True)
    date_of_decision = models.CharField(max_length=50, null=True, blank=True)
    transfer_est = models.CharField(max_length=50, null=True, blank=True)
    remarks = models.CharField(max_length=1024, null=True, blank=True)
    report_year = models.IntegerField()
    report_month=models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    organization= models.ForeignKey(auth_models.Organization, on_delete= models.SET_NULL, null=True, related_name='disposed_caseses_reports')
    created_by = models.ForeignKey('auth.User', related_name='disposed_caseses_reports_creator', on_delete=models.CASCADE)
    updated_by = models.ForeignKey('auth.User', related_name='disposed_caseses_reports_updator', null=True, on_delete=models.SET_NULL)
    history = AuditlogHistoryField()
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['case_no', 'report_year', 'report_month', 'organization'],
                name='unique_disposed_case_org_year_month'
            )
        ]
auditlog.register(DisposedCasesReport)

class PendingCasesReport(models.Model):

    date_of_inst = models.DateField(null=True, blank=True)
    case_no =  models.CharField(max_length=50, null=True, blank=True)
    case_title = models.CharField(max_length=1024, null=True, blank=True)
    case_type = models.CharField(max_length=1024, null=True, blank=True)
    # case_type = models.ForeignKey(CaseType,null=True,on_delete=models.SET_NULL, related_name="pending_case")
    civil_criminal = models.CharField(max_length=50, null=True, blank=True)
    brief_note = models.CharField(max_length=1024, null=True, blank=True)
    status = models.CharField(max_length=1024, null=True, blank=True)
    report_year = models.IntegerField()
    report_month=models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    organization= models.ForeignKey(auth_models.Organization, on_delete= models.SET_NULL, null=True, related_name='pending_caseses_reports')
    created_by = models.ForeignKey('auth.User', related_name='pending_caseses_reports_creator', on_delete=models.CASCADE)
    updated_by = models.ForeignKey('auth.User', related_name='pending_caseses_reports_updator', null=True, on_delete=models.SET_NULL)
    history = AuditlogHistoryField()
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['case_no', 'report_year', 'report_month', 'organization'],
                name='unique_pending_case_org_year_month'
            )
        ]
auditlog.register(PendingCasesReport)

class StatementOfCourtFeesFines(models.Model):
    report_year = models.IntegerField()
    report_month=models.CharField(max_length=100, null=True, blank=True)
    court_fees_collected=models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    fines_collected=models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    misc_collected=models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    # total_amount=models.DecimalField(max_digits=12, decimal_places=2, null=True)
    organization= models.ForeignKey(auth_models.Organization, on_delete= models.SET_NULL, null=True, related_name='state_ment_of_court_fees_fines')
    created_by = models.ForeignKey('auth.User', related_name='state_ment_of_court_fees_fines_creator', on_delete=models.CASCADE)
    updated_by = models.ForeignKey('auth.User', related_name='state_ment_of_court_fees_fines_updator', null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = AuditlogHistoryField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['report_year', 'report_month', 'organization'],
                name='unique_court_fees_org_year_month'
            )
        ]
auditlog.register(StatementOfCourtFeesFines)

class ListOfUndertrialPrisoners(models.Model):
    date_of_inst = models.DateField(null=True, blank=True)
    case_no =  models.CharField(max_length=50, null=True, blank=True)
    prosecution = models.CharField(max_length=1024, null=True, blank=True)
    name_of_the_accused = models.CharField(max_length=1024, null=True, blank=True)
    where_about_the_accused=models.CharField(max_length=1024, null=True, blank=True)
    in_custody_from=models.DateField(null=True, blank=True)
    report_year = models.IntegerField()
    report_month=models.CharField(max_length=100, null=True, blank=True)
    organization= models.ForeignKey(auth_models.Organization, on_delete= models.SET_NULL, null=True, related_name='list_of_undertrial_prisoners')
    remarks = models.CharField(max_length=1024, null=True, blank=True)
    created_by = models.ForeignKey('auth.User', related_name='under_trial_prisoner_created_by', on_delete=models.CASCADE)
    updated_by = models.ForeignKey('auth.User', related_name='under_trial_prisoner_updated_by', null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = AuditlogHistoryField()
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['case_no', 'report_year', 'report_month', 'organization'],
                name='unique_under_trial_prisoner_case_org_year_month'
            )
        ]
auditlog.register(ListOfUndertrialPrisoners)

class PendingCasesPartiesAboveSixty(models.Model):
    date_of_inst = models.DateField(null=True, blank=True)
    case_no =  models.CharField(max_length=50, null=True, blank=True)
    case_title = models.CharField(max_length=1024, null=True, blank=True)
    case_type = models.CharField(max_length=1024, null=True, blank=True)
    # case_type = models.ForeignKey(CaseType,null=True,on_delete=models.SET_NULL, related_name="pending_case")
    civil_criminal = models.CharField(max_length=50, null=True, blank=True)
    age_of_party=models.IntegerField(null=True, blank=True)
    report_year = models.IntegerField()
    report_month=models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    organization= models.ForeignKey(auth_models.Organization, on_delete= models.SET_NULL, null=True, related_name='pending_caseses_parties_above_sixties')
    created_by = models.ForeignKey('auth.User', related_name='pending_caseses_parties_above_sixties_creator', on_delete=models.CASCADE)
    updated_by = models.ForeignKey('auth.User', related_name='pending_caseses_parties_above_sixties_updator', null=True, on_delete=models.SET_NULL) 
    history = AuditlogHistoryField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['case_no', 'report_year', 'report_month', 'organization'],
                name='unique_pending_above_sixty_case_org_year_month'
            )
        ]
auditlog.register(PendingCasesPartiesAboveSixty)

class ExParteInjunctionCasesReport(models.Model):
    date_of_inst = models.DateField(null=True, blank=True)
    case_no =  models.CharField(max_length=50, null=True, blank=True)
    case_title = models.CharField(max_length=1024, null=True, blank=True)
    case_type = models.CharField(max_length=1024, null=True, blank=True)
    # case_type = models.ForeignKey(CaseType,null=True,on_delete=models.SET_NULL, related_name="pending_case")
    civil_criminal = models.CharField(max_length=50, null=True, blank=True)
    brief_note = models.CharField(max_length=1024, null=True, blank=True)
    status = models.CharField(max_length=1024, null=True, blank=True)
    duration_pending=models.IntegerField(null=True, blank=True)
    report_year = models.IntegerField()
    report_month=models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    organization= models.ForeignKey(auth_models.Organization, on_delete= models.SET_NULL, null=True, related_name='expaarte_injunction_reports')
    created_by = models.ForeignKey('auth.User', related_name='expaarte_injunction_creator', on_delete=models.CASCADE)
    updated_by = models.ForeignKey('auth.User', related_name='expaarte_injunction_updator', null=True, on_delete=models.SET_NULL)
    history = AuditlogHistoryField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['case_no', 'report_year', 'report_month', 'organization'],
                name='unique_exparte_case_org_year_month'
            )
        ]
auditlog.register(ExParteInjunctionCasesReport)

class LongPendingCasesReport(models.Model):
    date_of_inst = models.DateField(null=True, blank=True)
    case_no =  models.CharField(max_length=50, null=True, blank=True)
    case_title = models.CharField(max_length=1024, null=True, blank=True)
    case_type = models.CharField(max_length=1024, null=True, blank=True)
    # case_type = models.ForeignKey(CaseType,null=True,on_delete=models.SET_NULL, related_name="pending_case")
    civil_criminal = models.CharField(max_length=50, null=True, blank=True)
    brief_note = models.CharField(max_length=1024, null=True, blank=True)
    status = models.CharField(max_length=1024, null=True, blank=True)
    duration_pending=models.IntegerField(null=True, blank=True)
    report_year = models.IntegerField()
    report_month=models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    organization= models.ForeignKey(auth_models.Organization, on_delete= models.SET_NULL, null=True, related_name='long_pending_caseses_reports')
    created_by = models.ForeignKey('auth.User', related_name='long_pending_caseses_reports_creator', on_delete=models.CASCADE)
    updated_by = models.ForeignKey('auth.User', related_name='long_pending_caseses_reports_updator', null=True, on_delete=models.SET_NULL)
    history = AuditlogHistoryField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['case_no', 'report_year', 'report_month', 'organization'],
                name='unique_long_pending_case_org_year_month'
            )
        ]

class PartiesUnderVulnerableGroupCasesReport(models.Model):
    date_of_inst = models.DateField(null=True, blank=True)
    case_no =  models.CharField(max_length=50, null=True, blank=True)
    case_title = models.CharField(max_length=1024, null=True, blank=True)
    case_type = models.CharField(max_length=1024, null=True, blank=True)
    # case_type = models.ForeignKey(CaseType,null=True,on_delete=models.SET_NULL, related_name="pending_case")
    civil_criminal = models.CharField(max_length=50, null=True, blank=True)
    brief_note = models.CharField(max_length=1024, null=True, blank=True)
    status = models.CharField(max_length=1024, null=True, blank=True)
    vulnerable_group=models.CharField(max_length=255, null=True, blank=True)
    report_year = models.IntegerField()
    report_month=models.CharField(max_length=100,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    organization= models.ForeignKey(auth_models.Organization, on_delete= models.SET_NULL, null=True, related_name='parties_under_vulnerable_group_reports')
    created_by = models.ForeignKey('auth.User', related_name='parties_under_vulnerable_group_reports_creator', on_delete=models.CASCADE)
    updated_by = models.ForeignKey('auth.User', related_name='parties_under_vulnerable_group_reports_updator', null=True, on_delete=models.SET_NULL)
    history = AuditlogHistoryField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['case_no', 'report_year', 'report_month', 'organization'],
                name='unique_vulnerable_group_case_org_year_month'
            )
        ]
auditlog.register(LongPendingCasesReport)




