from django.urls import path

from .views import (
    AccountActivateView,
    AccountLoginView,
    AccountLogoutView,
    AccountMeView,
    AccountRegisterView,
)

app_name = "accounts"

urlpatterns = [
    path("register/", AccountRegisterView.as_view(), name="register"),
    path("login/", AccountLoginView.as_view(), name="login"),
    path("logout/", AccountLogoutView.as_view(), name="logout"),
    path("me/", AccountMeView.as_view(), name="me"),
    path("activate/", AccountActivateView.as_view(), name="activate"),
]
