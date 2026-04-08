from django.urls import path

from . import ui_views

app_name = "accounts-ui"

urlpatterns = [
    path("register/", ui_views.register_page, name="register"),
    path("login/", ui_views.login_page, name="login"),
    path("verify-email/<str:token>/", ui_views.verify_email_page, name="verify-email"),
    path("me/", ui_views.profile_page, name="profile"),
    path(
        "password-reset/",
        ui_views.password_reset_request_page,
        name="password-reset-request",
    ),
    path(
        "password-reset/done/",
        ui_views.password_reset_request_done_page,
        name="password-reset-request-done",
    ),
    path(
        "password-reset/confirm/<str:token>/",
        ui_views.password_reset_confirm_page,
        name="password-reset-confirm",
    ),
    path(
        "password-reset/success/",
        ui_views.password_reset_success_page,
        name="password-reset-success",
    ),
    path("me/nutrition/",
         ui_views.nutritional_profile_page,
         name="nutritional-profile"),
]
