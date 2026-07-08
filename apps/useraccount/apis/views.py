import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import ForgotPasswordSerializer, ProfileSerializer, RegisterSerializer, UpdateProfileSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer
from django.shortcuts import get_object_or_404
from apps.post.models import Follow
from apps.useraccount.models import User, otp
from django.core.mail import send_mail
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
class RegisterAPIView(APIView):
# /api/accounts/register/
    serializer_class = RegisterSerializer
    def post(self, request):

        serializer = RegisterSerializer(
            data=request.data
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                {
                    "message":
                    "User registered successfully."
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginAPIView(APIView):
    # /api/accounts/login/
    '''{
        "username": "muskan",
        "password": "Test@123"
    }'''
    serializer_class = LoginSerializer 
    authentication_classes = []

    permission_classes = []

    def post(self, request):

        serializer = LoginSerializer(
            data=request.data
        )

        if serializer.is_valid():

            user = serializer.validated_data["user"]

            refresh = RefreshToken.for_user(user)

            return Response(

                {

                    "message": "Login Successful",

                    "access": str(refresh.access_token),

                    "refresh": str(refresh),

                    "user": {

                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "gender": user.gender,

                    }

                },

                status=status.HTTP_200_OK

            )

        return Response(

            serializer.errors,

            status=status.HTTP_400_BAD_REQUEST

        )
class ProfileAPIView(APIView):
# /api/accounts/profile/id=1
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description="User ID",
            )
        ],
        responses=ProfileSerializer,
    )
    def get(self, request):

        id = request.query_params.get("id")

        if not id:

            return Response(
                {
                    "error": "id is required"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = get_object_or_404(
            User,
            id=id
        )

        serializer = ProfileSerializer(user)

        data = serializer.data

        data["is_following"] = Follow.objects.filter(
            follower=request.user,
            following=user
        ).exists()

        return Response(data)
    

class UpdateProfileAPIView(APIView):
#/api/accounts/update-profile/
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateProfileSerializer
    def patch(self, request):

        serializer = UpdateProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors)
    

class LogoutView(APIView):

    permission_classes = [IsAuthenticated]

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

    permission_classes = [IsAuthenticated]
    serializer_class = ForgotPasswordSerializer
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
    