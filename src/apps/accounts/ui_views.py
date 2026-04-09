from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_GET


@require_GET
def register_page(request):
    return render(request, "accounts/register.html")


@require_GET
def login_page(request):
    return render(request, "accounts/login.html")


@require_GET
def verify_email_page(request, token: str):
    return render(request, "accounts/verify_email.html", {"token": token})


@require_GET
@login_required
def profile_page(request):
    return render(request, "accounts/profile.html")


@require_GET
def password_reset_request_page(request):
    return render(request, "accounts/password_reset_request.html")


@require_GET
def password_reset_request_done_page(request):
    return render(request, "accounts/password_reset_request_done.html")


@require_GET
def password_reset_confirm_page(request, token: str):
    return render(request, "accounts/password_reset_confirm.html", {"token": token})


@require_GET
def password_reset_success_page(request):
    return render(request, "accounts/password_reset_success.html")

@require_GET
@login_required
def nutritional_profile_page(request):
    return render(request, "accounts/nutritional_profile.html")
