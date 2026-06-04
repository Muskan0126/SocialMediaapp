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

    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter your user name'}))

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'})
    )


class ForgotPasswordForm(forms.Form):

    email = forms.EmailField(required=True)


class ResetPasswordForm(forms.Form):

    otp = forms.CharField(max_length=6)

    new_password = forms.CharField(
        widget=forms.PasswordInput()
    )