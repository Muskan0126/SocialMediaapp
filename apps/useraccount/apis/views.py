from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.tokens import RefreshToken
import random
from django.core.mail import send_mail
from django.utils import timezone
from apps.useraccount.models import otp,User
from apps.useraccount.apis.serializers import (SignupSerializer,ForgotPasswordSerializer,ResetPasswordSerializer)

def get_tokens_for_user(user):

    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
@method_decorator(csrf_exempt, name='dispatch')
class SignupView(APIView):
    def post(self, request):
    
        serializer = SignupSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "User created successfully"
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class LoginView(APIView):

    def post(self, request):

        username = request.data.get("username")
        password = request.data.get("password")

        if not username:
            return Response(
                {"error": "Username is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not password:
            return Response(
                {"error": "Password is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is None:
            return Response(
                {"error": "Invalid username or password"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        tokens = get_tokens_for_user(user)

        return Response(
            {
                "message": "Login successful",
                "username": user.username,
                "access": tokens["access"],
                "refresh": tokens["refresh"]
            },
            status=status.HTTP_200_OK
        )

@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "Logout successful"},
                status=status.HTTP_200_OK
            )

        except Exception:
            return Response(
                {"error": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST
            )

class ForgotPasswordView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data["email"]

        otp_text = str(
            random.randint(
                100000,
                999999
            )
        )

        otp.objects.filter(
            email__email=email
        ).delete()

        try:
            # 1. Look up the User object using the email string
            user_instance = User.objects.get(email=email)
            
            # 2. Pass the actual User object to the ForeignKey field
            otp.objects.create(email=user_instance, otp=otp_text)

        except User.DoesNotExist:
            # Handle the error if the user does not exist in the system
            return Response(
            {"error": "No user account found with this email address."}, 
            status=status.HTTP_404_NOT_FOUND
        )

        send_mail(
            subject="Password Reset OTP",
            message=f"Your OTP is {otp_text}. Valid for 10 minutes.",
            from_email=None,
            recipient_list=[email],
            fail_silently=False
        )

        return Response(
            {
                "message":
                "OTP sent successfully"
            },
            status=status.HTTP_200_OK
        )
    
class ResetPasswordView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = ResetPasswordSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]
        new_password = serializer.validated_data["new_password"]

        try:

            otp_record = otp.objects.get(
                email=email,
                otp=otp
            )

        except otp.DoesNotExist:

            return Response(
                {
                    "error": "Invalid OTP"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if otp_record.is_expired():

            otp_record.delete()

            return Response(
                {
                    "error": "OTP expired"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.get(
            email=email
        )

        user.set_password(
            new_password
        )

        user.save()

        otp_record.delete()

        return Response(
            {
                "message":
                "Password reset successful"
            },
            status=status.HTTP_200_OK
        )