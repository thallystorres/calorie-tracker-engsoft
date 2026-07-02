import uuid
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from apps.contents.dependencies import get_content_repository
from .dependencies import get_study_tracker_service, get_study_session_repository

@require_http_methods(["GET"])
@login_required
def tracker_page(request):
    contents = get_content_repository().list_contents()
    return render(request, "study_tracker/tracker.html", {"contents": contents})

@require_http_methods(["GET"])
@login_required
def tracker_dashboard_partial(request):
    repo = get_study_session_repository()
    profile = getattr(request.user, "study_profile", None)

    if not profile:
        return render(request, "study_tracker/partials/dashboard.html", {"profile_required": True})

    today = timezone.localdate()
    totals = repo.get_daily_totals(user=request.user, date=today)
    total_minutes = totals.get("total_minutes") or 0

    return render(request, "study_tracker/partials/dashboard.html", {
        "profile_required": False,
        "target_weekly": profile.target_weekly_minutes,
        "total_minutes_today": total_minutes,
        "target_score": profile.target_quiz_score,
    })

@require_http_methods(["GET"])
@login_required
def add_study_item_partial(request):
    # Gera um ID único para evitar conflitos de names no formulário array
    unique_id = uuid.uuid4().hex[:6]
    contents = get_content_repository().list_contents()
    return render(request, "study_tracker/partials/study_item_form.html", {
        "uid": unique_id,
        "contents": contents
    })

@require_http_methods(["POST"])
@login_required
def save_session(request):
    service = get_study_tracker_service()
    content_repo = get_content_repository()

    # Processando os arrays do formulário
    strategy = request.POST.get("strategy")
    content_ids = request.POST.getlist("content_id")
    times = request.POST.getlist("time_minutes")
    notes_list = request.POST.getlist("notes")

    items_data = []
    for c_id, time_val, note in zip(content_ids, times, notes_list):
        if c_id and time_val:
            content = content_repo.get_by_id(int(c_id))
            if content:
                items_data.append({
                    "content": content,
                    "time_minutes": int(time_val),
                    "notes": note.strip()
                })

    validated_data = {"strategy": strategy, "items": items_data}
    session, warnings = service.log_session(user=request.user, validated_data=validated_data)

    # Renderiza a resposta passando as mensagens de aviso e adicionando um header
    # do HTMX (HX-Trigger) para forçar a atualização automática do dashboard
    response = render(request, "study_tracker/partials/session_feedback.html", {
        "warnings": warnings,
        "success": True
    })
    response["HX-Trigger"] = "sessionSaved"
    return response
