import random

from django.shortcuts import render, redirect
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    get_user_model
)
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib import messages
from django.views import View

from .forms import (
    SignupForm,
    LoginForm,
    ForgotPasswordForm,
    ResetPasswordForm
)

from .models import otp

User = get_user_model()

class signup_view(View):
    def get(self,request):

        form = SignupForm()
        return render(
        request,
        "useraccount/signup.html",
        {"form": form}
    )
    def post(self,request):
    
        form = SignupForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            messages.success(request, "Account created successfully.")
            return redirect("login")

        return render(
            request,
            "useraccount/signup.html",
            {"form": form}
        )


class login_view(View):
    def get(self,request):

        form = LoginForm()
        return render(
            request,
            "useraccount/login.html",
            {"form": form}
        )
    def post(self,request):
        form = LoginForm(request.POST)

        if form.is_valid():

            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user:

                login(request, user)

                return redirect("home")

            messages.error(
                request,
                "Invalid username or password."
            )

        return render(
            request,
            "useraccount/login.html",
            {"form": form}
        )


def logout_view(request):

    logout(request)

    messages.success(
        request,
        "Logged out successfully."
    )

    return redirect("login")


class forgot_password_view(View):
    def get(self,request):
        form = ForgotPasswordForm()
        return render(
            request,
            "useraccount/forgot_password.html",
            {"form": form}
        )
    def post(self, request):

        form = ForgotPasswordForm(request.POST)

        if form.is_valid():

            email = form.cleaned_data["email"]

            try:

                user = User.objects.get(email=email)

            except User.DoesNotExist:

                messages.error(
                    request,
                    "No account found with this email."
                )

                return render(
                    request,
                    "useraccount/forgot_password.html",
                    {"form": form}
                )

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
                user_instance = User.objects.get(email=email)
                otp.objects.create(email=user_instance, otp=otp_text)

            except User.DoesNotExist:
                messages.error(
                    request,
                    "No account found with this email."
                )

            send_mail(
                subject="Password Reset OTP",
                message=f"Your OTP is {otp_text}. Valid for 10 minutes.",
                from_email=None,
                recipient_list=[email],
                fail_silently=False
            )

            request.session["reset_email"] = email

            messages.success(
                request,
                "OTP sent successfully."
            )

            return redirect("reset_password")

        return render(
            request,
            "useraccount/forgot_password.html",
            {"form": form}
        )


class reset_password_view(View):
    def get(self,request):
        form = ResetPasswordForm()
        return render(
            request,
            "useraccount/reset_password.html",
            {"form": form}
        )
    def post(self,request):

        form = ResetPasswordForm(request.POST)

        if form.is_valid():

            otp_text = form.cleaned_data["otp"]

            new_password = form.cleaned_data[
                "new_password"
            ]

            email = request.session.get(
                "reset_email"
            )

            if not email:

                messages.error(
                    request,
                    "Session expired. Try again."
                )

                return redirect(
                    "forgot_password"
                )

            try:

                otp_record = (
                    otp.objects.get(
                        email__email=email,
                        otp=otp_text
                    )
                )

            except otp.DoesNotExist:

                messages.error(
                    request,
                    "Invalid OTP."
                )

                return render(
                    request,
                    "useraccount/reset_password.html",
                    {"form": form}
                )

            if otp_record.is_expired():

                otp_record.delete()

                messages.error(
                    request,
                    "OTP has expired."
                )

                return redirect(
                    "forgot_password"
                )

            user = User.objects.get(
                email=email
            )

            user.set_password(
                new_password
            )

            user.save()

            otp_record.delete()

            request.session.pop(
                "reset_email",
                None
            )

            messages.success(
                request,
                "Password reset successfully."
            )

            return redirect("login")

        return render(
            request,
            "useraccount/reset_password.html",
            {"form": form}
        )



class home_view(View):
    def get(self,request):
        return render(
            request,
            "useraccount/home.html"
        )