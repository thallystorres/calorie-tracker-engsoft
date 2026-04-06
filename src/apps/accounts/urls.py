from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.generic import TemplateView

from .views import (
    AccountActivateView,
    AccountLoginView,
    AccountLogoutView,
    AccountMeView,
    AccountRegisterView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
)

app_name = "accounts"

urlpatterns = [
    path(
        "register-ui/",
        TemplateView.as_view(template_name="accounts/register.html"),
        name="register-ui",
    ),
    path(
        "login-ui/",
        TemplateView.as_view(template_name="accounts/login.html"),
        name="login-ui",
    ),
    path(
        "activate-ui/",
        TemplateView.as_view(template_name="accounts/activate.html"),
        name="activate-ui",
    ),
    path(
        "profile-ui/",
        login_required(TemplateView.as_view(template_name="accounts/profile.html")),
        name="profile-ui",
    ),
    path("register/", AccountRegisterView.as_view(), name="register"),
    path("login/", AccountLoginView.as_view(), name="login"),
    path("logout/", AccountLogoutView.as_view(), name="logout"),
    path("me/", AccountMeView.as_view(), name="me"),
    path("activate/", AccountActivateView.as_view(), name="activate"),
    path(
        "password-reset/request/",
        PasswordResetRequestView.as_view(),
        name="password-reset-request",
    ),
    path(
        "password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
]
