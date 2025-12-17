from django.db import models
from django.contrib.auth.models import User, Group

# Create your models here.
class OrganizationType(models.Model):
    org_type_name=models.CharField(max_length=256)
    org_type_short_name=models.CharField(max_length=50)

    def __str__(self):
        return f"{self.org_type_short_name}({self.org_type_name})"

class Organization(models.Model):
    organization_type = models.ForeignKey(OrganizationType, null=True, on_delete=models.SET_NULL)
    organization_name= models.CharField(max_length=256)
    organization_shortname = models.CharField(max_length=128, null= True)
    district_code = models.CharField(max_length=10, null= False)
    parent_org = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='org_children',
        on_delete=models.CASCADE
    )
    def __str__(self):
        return f"{self.organization_name}({self.district_code})"

class UserProfile(models.Model):
    user = models.OneToOneField(User, null=False, on_delete=models.CASCADE, related_name='user_profile')
    organization = models.ForeignKey(Organization, null= True, on_delete=models.SET_NULL, related_name='user_profile')

    def __str__(self):
        return f"{self.user.username} - ({self.organization.organization_name})"

