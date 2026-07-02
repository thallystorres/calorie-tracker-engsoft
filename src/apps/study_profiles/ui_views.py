from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from .models import StudyProfile
from .dependencies import get_study_profile_service

@require_http_methods(["GET"])
@login_required
def profile_page(request):
    profile = getattr(request.user, "study_profile", None)
    return render(request, "study_profiles/profile.html", {"profile": profile})

@require_http_methods(["POST"])
@login_required
def save_profile(request):
    service = get_study_profile_service()
    profile = getattr(request.user, "study_profile", StudyProfile(user=request.user))

    data = {
        "goal": request.POST.get("goal"),
        "weekly_availability_hours": int(request.POST.get("weekly_availability_hours", 10)),
        "focus_limit_minutes": int(request.POST.get("focus_limit_minutes", 60)),
    }

    service.upsert_profile(profile, data)

    # Retorna uma mensagem de sucesso via HTMX
    return render(request, "study_profiles/partials/success_message.html", {
        "message": "Perfil atualizado com sucesso!"
    })
