from django.urls import path

from apps.useraccount.apis.views import ForgotPasswordView, LoginAPIView, LogoutView, ProfileAPIView, RegisterAPIView, UpdateProfileAPIView

urlpatterns = [
 path("register/",RegisterAPIView.as_view(), name="register-api"), #/api/accounts/register/
 path("login/", LoginAPIView.as_view(), name="login-api"), #/api/accounts/login/
 path("logout/", LogoutView.as_view(), name="logout-api"), #/api/accounts/logout/
 path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"), #/api/accounts/forgot-password/
 path("profile/", ProfileAPIView.as_view(), name="profile-api"), #/api/accounts/profile/
 path("update-profile/", UpdateProfileAPIView.as_view(), name="update-profile-api"), #/api/accounts/update-profile/
]