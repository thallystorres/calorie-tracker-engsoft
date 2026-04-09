from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_GET


@require_GET
@login_required
def food_create_page(request):
    return render(request, "foods/new_food.html")
