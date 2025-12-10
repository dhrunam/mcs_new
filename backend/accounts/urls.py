from django.urls import path, include
from accounts.views import RegisterView, UserList, OrganizationList, UserSingle, UserInfo, OrganizationDetailView
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('user/', UserList.as_view(), name='users'),
    path('user/<int:pk>', UserSingle.as_view(), name='users_single'),
    path('user_info', UserInfo.as_view(), name='users_single'),
    path('organization/', OrganizationList.as_view(), name='organization'),
    path('organization/<int:id>', OrganizationDetailView.as_view(), name='organization_detail'),
    path('auth/', include('durin.urls')),
]