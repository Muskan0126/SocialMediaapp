from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import ProfileSerializer, RegisterSerializer, UpdateProfileSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer
from django.shortcuts import get_object_or_404
from apps.post.models import Follow
from apps.useraccount.models import User

class RegisterAPIView(APIView):
# /api/accounts/register/

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