from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from apps.common.validators import validate_image
from apps.common.validators import validate_image
from apps.post.models import Follow, Post
import re

User = get_user_model()
# /api/accounts/register/
'''
{
    "username": "muskan",
    "email": "muskan11@gmail.com",
    "password": "Test@123",
    "confirm_password": "Test@123",
    "first_name": "Muskan",
    "last_name": "Agrawal",
    "phone_no": "9876543210",
    "gender": "F"
}
'''
class RegisterSerializer(serializers.ModelSerializer):

    confirm_password = serializers.CharField(
        write_only=True
    )
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "confirm_password",
            "first_name",
            "last_name",
            "phone_no",
            "gender",
            "country",
            
        ]

        extra_kwargs = {
            "password": {
                "write_only": True
            }
        }

    def validate_username(self, value):

        if not re.match(r"^[a-z][a-z0-9_]*$", value):
            raise serializers.ValidationError(
                "Capital letters not allowed."
            )

        if User.objects.filter(
            username=value
        ).exists():

            raise serializers.ValidationError(
                "Username already exists."
            )

        return value

    def validate_email(self, value):

        if User.objects.filter(
            email=value
        ).exists():

            raise serializers.ValidationError(
                "Email already exists."
            )

        return value

    def validate_phone_no(self, value):

        if len(str(value)) != 10:
            raise serializers.ValidationError(
                "Please enter a valid 10 digit phone number."
            )

        return value

    def validate_gender(self, value):

        if value not in ["M", "F", "O"]:
            raise serializers.ValidationError(
                "Gender must be M, F or O."
            )

        return value

    def validate(self, attrs):

        if attrs["password"] != attrs["confirm_password"]:

            raise serializers.ValidationError(
                {
                    "confirm_password":
                    "Passwords do not match."
                }
            )

        return attrs

    def create(self, validated_data):

        validated_data.pop("confirm_password")

        password = validated_data.pop("password")

        user = User(**validated_data)

        user.set_password(password)

        user.save()

        return user
    
class LoginSerializer(serializers.Serializer):

    username = serializers.CharField()

    password = serializers.CharField(
        write_only=True
    )

    def validate(self, attrs):

        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(
            username=username,
            password=password
        )

        if not user:

            raise serializers.ValidationError(
                "Invalid username or password."
            )

        attrs["user"] = user

        return attrs
class ProfileSerializer(serializers.ModelSerializer):

    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()
    posts = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "bio",
            "profile_photo",
            "followers",
            "following",
            "posts",
        ]

    def get_followers(self, obj):
        return Follow.objects.filter(
            following=obj
        ).count()

    def get_following(self, obj):
        return Follow.objects.filter(
            follower=obj
        ).count()

    def get_posts(self, obj):
        return Post.objects.filter(
            user=obj
        ).count()
    
class UpdateProfileSerializer(serializers.ModelSerializer):
    profile_photo = serializers.ImageField(
        validators=[validate_image],
        required=False
    )
    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_no",
            "bio",
            "gender",
            "country",
            "profile_photo",
        ]

    def validate_username(self, value):

        if not re.match(r"^[a-z][a-z0-9_]*$", value):
            raise serializers.ValidationError(
                "Username must contain only lowercase letters, numbers and underscores."
            )

        user = self.instance

        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError(
                "Username already exists."
            )

        return value

    def validate_email(self, value):

        user = self.instance

        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError(
                "Email already exists."
            )

        return value

    def validate_phone_no(self, value):

        if len(str(value)) != 10:
            raise serializers.ValidationError(
                "Enter a valid 10 digit phone number."
            )

        user = self.instance

        if User.objects.exclude(pk=user.pk).filter(phone_no=value).exists():
            raise serializers.ValidationError(
                "Phone number already exists."
            )

        return value

    def validate_gender(self, value):

        if value not in ["M", "F", "O"]:
            raise serializers.ValidationError(
                "Gender must be M, F or O."
            )

        return value
    
class ForgotPasswordSerializer(serializers.Serializer):

    email = serializers.EmailField()

    def validate_email(self, value):

        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "No account found with this email."
            )

        return value
