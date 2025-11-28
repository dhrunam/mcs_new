from django.contrib.auth.models import User
from rest_framework import generics, response, status, views
from rest_framework.permissions import AllowAny
from accounts.serializers import RegisterSerializer, UserSerializer
from accounts import models as auth_models, serializers as auth_serializers
from django.db import transaction
from accounts import models as auth_models

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        try:
          
            user = User.objects.create(
                        username=self.request.data.get('username'),
                        first_name=self.request.data.get('first_name'),
                        last_name = self.request.data.get('last_name'),
                        email = self.request.data.get('email'),
                       
                        # is_staff=True if self.request.data['group'] == 'general_user' else False,
                    )
            # user.groups.add(Group.objects.get(
            #             name=self.request.data['group']))
            user.set_password(self.request.data['password'])
            user.save()

            user_profile = auth_models.UserProfile.objects.update_or_create(
                        user=user,
                        defaults={
                           
                            "organization": auth_models.Organization.objects.get(pk=request.data.get('organization')) if  request.data.get('organization', False) else None,

                        }
            )
            
           
            # self.create(self, request, *args, **kwargs)
            return response.Response("User created sucessfully", status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return response.Response("Some error occured. Please try again", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class UserList(generics.ListAPIView):
    queryset = User.objects.prefetch_related('groups')
    serializer_class = auth_serializers.LeanUserSerializer


    def get_queryset(self):
        queryset = User.objects.all()
        print('User', self.request.user)
        user_group= self.request.query_params.get('user_group')
        if user_group:
             return queryset.filter(groups__name=user_group)
        else:
            queryset = queryset.filter(id= self.request.user.id)

        return queryset
    
class UserSingle(generics.RetrieveAPIView):
    queryset = User.objects.prefetch_related('groups')
    serializer_class = auth_serializers.LeanUserSerializer
    def get_queryset(self):
        queryset = User.objects.all()
        
        user_group= self.request.query_params.get('user_group')
        if user_group:
             return queryset.filter(groups__name=user_group)
        else:
            queryset = queryset.filter(id= self.request.user.id)

        return queryset
    
class UserInfo(views.APIView):
#    permission_classes = [IsAuthenticated]  # Ensures that the user is authenticated

    def get(self, request):
        # Retrieve the currently logged-in user
        user = request.user
        print("user:", user)
        # Serialize the user information
        if user:
            serializer = auth_serializers.LeanUserSerializer(user)
        
        # Return the user data
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return response.Response("User not found", status=status.HTTP_200_OK)

    

