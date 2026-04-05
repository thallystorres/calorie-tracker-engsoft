from django.urls import path

from .views import (
    AccountRegisterView,
)

app_name = "accounts"

urlpatterns = [path("register/", AccountRegisterView.as_view(), name="register")]
