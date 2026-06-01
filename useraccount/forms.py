from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class SignupForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput()
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "phone_no",
            "gender",
        ]


class LoginForm(forms.Form):

    username = forms.CharField()

    password = forms.CharField(
        widget=forms.PasswordInput()
    )


class ForgotPasswordForm(forms.Form):

    email = forms.EmailField()


class ResetPasswordForm(forms.Form):

    otp = forms.CharField(max_length=6)

    new_password = forms.CharField(
        widget=forms.PasswordInput()
    )