from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .dependencies import (
    get_goals_service,
    get_volume_metrics_service,
    get_workout_repository,
)


@require_GET
@login_required
def academia_page(request):
    return render(request, "academia/academia.html")


@require_GET
@login_required
def volume_dashboard_partial(request):
    service = get_volume_metrics_service()
    breakdown = service.get_weekly_volume_breakdown(user=request.user)
    return render(
        request,
        "academia/partials/volume_dashboard.html",
        {"breakdown": breakdown},
    )


@require_GET
@login_required
def workout_history_partial(request):
    repo = get_workout_repository()
    sessions = repo.list_sessions_for_user(user=request.user)
    from rest_framework.pagination import PageNumberPagination
    paginator = PageNumberPagination()
    page = paginator.paginate_queryset(sessions, request, view=workout_history_partial)
    return render(
        request,
        "academia/partials/workout_history.html",
        {
            "page": page,
            "has_previous": paginator.page.has_previous() if page else False,
            "has_next": paginator.page.has_next() if page else False,
            "previous_page_number": paginator.page.previous_page_number() if page and paginator.page.has_previous() else None,
            "next_page_number": paginator.page.next_page_number() if page and paginator.page.has_next() else None,
            "count": paginator.page.paginator.count if page else 0,
        },
    )


@require_GET
@login_required
def goals_partial(request):
    service = get_goals_service()
    goals = service.get_active_goals(user=request.user)
    return render(
        request,
        "academia/partials/goals.html",
        {"goals": goals},
    )
