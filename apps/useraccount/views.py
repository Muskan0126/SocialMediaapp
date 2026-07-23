import random

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.views import View

from apps.common.logger import app_logger, error_logger, security_logger

from .forms import ForgotPasswordForm, LoginForm, ResetPasswordForm, SignupForm
from .models import otp

User = get_user_model()
"""This file contains all the views for the useraccount app
The views are class based views and function based views
The views are used to render the templates and handle the requests
The views are used to handle the signup, login, logout, forgot password, reset password, home, and other user account related functionalities
"""


class signup_view(View):
    """This contains the signup feature of the user information
    Allowed to create a new user account and also handle the signup form validation
    """

    app_logger.info("Signup form opened")

    def get(self, request):

        form = SignupForm()
        return render(request, "useraccount/signup.html", {"form": form})

    def post(self, request):

        form = SignupForm()
        form = SignupForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            app_logger.info("Signup completed for user: %s", user.username)
            return redirect("login")

        return render(request, "useraccount/signup.html", {"form": form})


class login_view(View):
    """This contains the login feature of the user information
    Allowed to login to the user account and also handle the login form validation.
    also handle the authentication of the user and redirect to the home page if successful"""

    def get(self, request):

        form = LoginForm()
        return render(request, "useraccount/login.html", {"form": form})

    def post(self, request):
        form = LoginForm(request.POST)

        if form.is_valid():

            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)

            if user:

                login(request, user)
                security_logger.info("Sign in completed for user: %s", user.username)
                return redirect("home")

            messages.error(request, "Invalid username or password.")

        return render(request, "useraccount/login.html", {"form": form})


def logout_view(request):

    logout(request)

    return redirect("login")


class forgot_password_view(View):
    """This contains the forgot password feature of the user information.
    Allowed to reset the password of the user account and also handle the forgot password form validation.
    also handle the sending of the OTP to the user's email and redirect to the reset password page"""

    def get(self, request):
        form = ForgotPasswordForm()
        return render(request, "useraccount/forgot_password.html", {"form": form})

    def post(self, request):

        form = ForgotPasswordForm(request.POST)

        if form.is_valid():

            email = form.cleaned_data["email"]

            try:

                user = User.objects.get(email=email)

            except User.DoesNotExist:

                messages.error(request, "No account found with this email.")

                return render(request, "useraccount/forgot_password.html", {"form": form})

            otp_text = str(random.randint(100000, 999999))

            otp.objects.filter(email__email=email).delete()

            try:
                user_instance = User.objects.get(email=email)
                otp.objects.create(email=user_instance, otp=otp_text)

            except User.DoesNotExist:
                messages.error(request, "No account found with this email.")

            send_mail(
                subject="Password Reset OTP",
                message=f"Your OTP is {otp_text}. Valid for 10 minutes.",
                from_email=None,
                recipient_list=[email],
                fail_silently=False,
            )

            request.session["reset_email"] = email

            messages.success(request, "OTP sent successfully.")

            return redirect("reset_password")

        return render(request, "useraccount/forgot_password.html", {"form": form})


class reset_password_view(LoginRequiredMixin, View):

    def get(self, request):

        user = request.user

        # Delete any old OTPs
        otp.objects.filter(email=user).delete()

        generated_otp = random.randint(100000, 999999)

        otp.objects.create(email=user, otp=str(generated_otp))

        send_mail(
            subject="Reset Password OTP",
            message=f"Your OTP is {generated_otp}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )

        form = ResetPasswordForm()

        return render(
            request,
            "useraccount/reset_password.html",
            {"form": form},
        )

    def post(self, request):

        form = ResetPasswordForm(request.POST)

        if form.is_valid():

            otp_text = form.cleaned_data["otp"]
            new_password = form.cleaned_data["new_password"]

            user = request.user
            email = user.email

            try:
                otp_record = otp.objects.get(email__email=email, otp=otp_text)

            except otp.DoesNotExist:
                messages.error(request, "Invalid OTP.")
                return render(
                    request,
                    "useraccount/reset_password.html",
                    {"form": form},
                )

            if otp_record.is_expired():
                otp_record.delete()
                messages.error(request, "OTP has expired.")
                return render(
                    request,
                    "useraccount/reset_password.html",
                    {"form": form},
                )

            user.set_password(new_password)
            user.save()

            otp_record.delete()

            messages.success(request, "Password reset successfully.")
            return redirect("profile_view")

        return render(
            request,
            "useraccount/reset_password.html",
            {"form": form},
        )


class home_view(View):
    def get(self, request):
        return render(request, "useraccount/home.html")
