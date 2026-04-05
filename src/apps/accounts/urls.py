from django.urls import path

from .views import (
    AccountLoginView,
    AccountRegisterView,
)

app_name = "accounts"

urlpatterns = [
    path("register/", AccountRegisterView.as_view(), name="register"),
    path("login/", AccountLoginView.as_view(), name="login"),
]
