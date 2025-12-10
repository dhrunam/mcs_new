from django.contrib.auth.models import User
from rest_framework import generics, response, status, views
from rest_framework.permissions import AllowAny
from accounts.serializers import RegisterSerializer, UserSerializer
from accounts import models as auth_models, serializers as auth_serializers
from django.db import transaction
from accounts import models as auth_models


class OrganizationList(generics.ListAPIView):

    queryset = auth_models.Organization.objects.all()
    serializer_class = auth_serializers.OrganizationSerializer
    pagination_class = None

class OrganizationDetailView(generics.RetrieveAPIView):

    queryset = auth_models.Organization.objects.all()
    serializer_class = auth_serializers.OrganizationSerializer
    lookup_field = 'id'
    
    
