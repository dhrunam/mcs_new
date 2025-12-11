from django.contrib import admin
from accounts import models as account_models

# Register your models here.

admin.site.register([account_models.Organization, account_models.OrganizationType, account_models.UserProfile])
