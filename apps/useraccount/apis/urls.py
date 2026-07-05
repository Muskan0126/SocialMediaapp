from django.urls import path

from apps.useraccount.apis.views import LoginAPIView, ProfileAPIView, RegisterAPIView, UpdateProfileAPIView

urlpatterns = [
 path("register/",RegisterAPIView.as_view(), name="register-api"), #/api/accounts/register/
 path("login/", LoginAPIView.as_view(), name="login-api"), #/api/accounts/login/
 path("profile/", ProfileAPIView.as_view(), name="profile-api"), #/api/accounts/profile/
 path("update-profile/", UpdateProfileAPIView.as_view(), name="update-profile-api"), #/api/accounts/update-profile/
]