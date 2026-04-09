from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_GET

from apps.foods.models import Food
from apps.tracker.models import Meal


@require_GET
@login_required
def tracker_page(request):
    foods = Food.objects.all().order_by("name")
    meals = (
        Meal.objects.filter(user=request.user)
        .prefetch_related("items__food")
        .order_by("-eaten_at")
    )
    return render(
        request,
        "tracker/tracker.html",
        {
            "foods": foods,
            "meals": meals,
        },
    )
