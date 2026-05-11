from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_GET

from apps.foods.dependencies import get_food_repository

from .dependencies import get_meal_repository


@require_GET
@login_required
def tracker_page(request):
    foods_repo = get_food_repository()
    foods = foods_repo.list_foods()
    return render(
        request,
        "tracker/tracker.html",
        {
            "foods": foods,
        },
    )


PROFILE_REQUIRED_CTX = {
    "profile_required": True,
    "profile_message": "Preencha seu perfil nutricional para ver o dashboard e o histórico.",
}


def _get_profile_or_message(user):
    profile = getattr(user, "nutritional_profile", None)
    if profile is None:
        return None, PROFILE_REQUIRED_CTX
    return profile, {}


def _parse_custom_dates(request) -> tuple[date | None, date | None]:
    start_raw = request.GET.get("start_date")
    end_raw = request.GET.get("end_date")
    if not start_raw or not end_raw:
        return None, None
    try:
        start_date = date.fromisoformat(start_raw)
        end_date = date.fromisoformat(end_raw)
    except ValueError:
        return None, None
    if start_date > end_date:
        return None, None
    return start_date, end_date


@require_GET
@login_required
def tracker_dashboard_partial(request):
    repo = get_meal_repository()
    profile, message_ctx = _get_profile_or_message(request.user)
    if not profile:
        return render(request, "tracker/partials/dashboard.html", message_ctx)

    today = timezone.localdate()
    totals = repo.get_daily_totals(user=request.user, date=today)
    consumed = totals.get("kcal") or 0
    remaining = (profile.daily_calorie_target or 0) - consumed

    return render(
        request,
        "tracker/partials/dashboard.html",
        {
            "profile_required": False,
            "daily_target": profile.daily_calorie_target,
            "consumed": consumed,
            "remaining": max(0, remaining),
            "macros": {
                "protein": totals.get("protein") or 0,
                "carbs": totals.get("carbs") or 0,
                "fat": totals.get("fat") or 0,
                "fiber": totals.get("fiber") or 0,
            },
        },
    )


@require_GET
@login_required
def tracker_history_partial(request):
    repo = get_meal_repository()
    profile, message_ctx = _get_profile_or_message(request.user)
    if not profile:
        return render(request, "tracker/partials/history.html", message_ctx)

    period = request.GET.get("period", "7")
    end_date = timezone.localdate()
    if period == "30":
        start_date = end_date - timedelta(days=30)
    elif period == "custom":
        start_date, end_date = _parse_custom_dates(request)
        if not start_date or not end_date:
            period = "7"
            end_date = timezone.localdate()
            start_date = end_date - timedelta(days=7)
    else:
        start_date = end_date - timedelta(days=7)

    daily_rows = repo.get_period_daily_totals(
        user=request.user,
        start_date=start_date,
        end_date=end_date,
    )

    return render(
        request,
        "tracker/partials/history.html",
        {
            "profile_required": False,
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "daily_rows": daily_rows,
        },
    )
