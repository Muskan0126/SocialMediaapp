from django.urls import path

from django.urls import path

from .views import (
    signup_view,
    login_view,
    logout_view,
    forgot_password_view,
    reset_password_view,
    home_view
)

urlpatterns = [ path(
        "",
        signup_view.as_view(),
        name="signup"),

    path(
        "login/",
        login_view.as_view(),
        name="login"
    ),

    path(
        "logout/",
        logout_view,
        name="logout"
    ),

    path(
        "forgot-password/",
        forgot_password_view.as_view(),
        name="forgot_password"
    ),

    path(
        "reset-password/",
        reset_password_view.as_view(),
        name="reset_password"
    ),

    path(
        "",
        home_view.as_view(),
        name="home"
    ),
]