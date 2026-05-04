from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_GET

from apps.foods.dependencies import get_food_repository

from .dependencies import get_meal_repository


@require_GET
@login_required
def tracker_page(request):
    meals_repo = get_meal_repository()
    foods_repo = get_food_repository()
    foods = foods_repo.list_foods()
    meals = meals_repo.get_meals_for_user(user=request.user)
    return render(
        request,
        "tracker/tracker.html",
        {
            "foods": foods,
            "meals": meals,
        },
    )
