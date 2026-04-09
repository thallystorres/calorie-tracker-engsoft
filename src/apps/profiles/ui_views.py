from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_GET


@require_GET
@login_required
def nutritional_profile_page(request):
    return render(request, "profiles/nutritional_profile.html")
