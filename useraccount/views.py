from django.contrib.auth import authenticate, login, logout

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import SignupSerializer
from rest_framework_simplejwt.tokens import RefreshToken

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



