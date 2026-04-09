from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .models import NutritionalProfile


@require_GET
@login_required
def nutritional_profile_page(request):
    try:
        profile = request.user.nutritional_profile
    except NutritionalProfile.DoesNotExist:
        profile = None

    return render(
        request,
        "profiles/nutritional_profile.html",
        {"profile": profile},
    )
