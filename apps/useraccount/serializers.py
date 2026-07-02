from rest_framework import serializers
from .models import User



class SignupSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username',
            'email',
            'password',
            'bio',
            'gender',
            'country',
            'phone_no'
            ]

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_email(self, value):
        if not value or User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Either Email not provided or Email already exists")

        return value

    def validate_phone_no(self, value):

        if not value or len(value)!=10:
            raise serializers.ValidationError(
            "Phone number is required and only 10 digits allowed")

        return value

    def validate_password(self, value):
        
        if not value or len(value) < 8 or value.isdigit():
            raise serializers.ValidationError("Password must contain at least 8 characters.")

        return value
    
    def validate_gender(self, value):
        
        if not value or value not in ('F','M','O'):
            raise serializers.ValidationError("Only F,M,O allowed")

        return value


    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user



class ForgotPasswordSerializer(serializers.Serializer):

    email = serializers.EmailField()

    def validate_email(self, value):

        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "No account found with this email."
            )

        return value


class ResetPasswordSerializer(serializers.Serializer):

    email = serializers.EmailField()

    otp = serializers.CharField(
        max_length=6
    )

    new_password = serializers.CharField(
        min_length=8
    )