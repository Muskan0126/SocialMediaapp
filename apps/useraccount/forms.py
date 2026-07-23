import re

from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

GENDER_CHOICES = [
    ("M", "Male"),
    ("F", "Female"),
    ("O", "Other"),
]


class SignupForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput())
    phone_no = forms.CharField(max_length=10, min_length=10)
    gender = forms.ChoiceField(choices=GENDER_CHOICES)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "phone_no",
            "gender",
        ]

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if not re.match(r"^[a-z][a-z0-9_.]*$", username):
            raise forms.ValidationError("Capital letters, spaces and special characters not allowed.")
        if username and (username[0].isdigit() or username[0] in ("@", "/", "-", "+")):
            raise forms.ValidationError("Username must start with a letter.")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password and (password.isdigit() or len(password) < 8):
            raise forms.ValidationError("Password must be at least 8 characters and contain letters and numbers.")
        return password

    def clean_phone_no(self):
        phone_no = self.cleaned_data.get("phone_no")
        if not phone_no or not phone_no.isdigit() or len(phone_no) != 10:
            raise forms.ValidationError("Enter a valid 10-digit phone number.")
        return phone_no


class LoginForm(forms.Form):

    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Enter your user name"}))

    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Enter your password"}))


class ForgotPasswordForm(forms.Form):

    email = forms.EmailField(required=True)


class ResetPasswordForm(forms.Form):

    otp = forms.CharField(max_length=6)

    new_password = forms.CharField(widget=forms.PasswordInput())
