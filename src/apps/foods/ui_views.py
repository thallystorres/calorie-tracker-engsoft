from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_GET

from apps.foods.models import Food, MealLog


@require_GET
@login_required
def tracker_page(request):
    foods = Food.objects.all().order_by("name")
    meal_logs = MealLog.objects.filter(user=request.user).order_by("-consumed_at")
    return render(
        request, "foods/tracker.html", {"foods": foods, "meal_logs": meal_logs}
    )
