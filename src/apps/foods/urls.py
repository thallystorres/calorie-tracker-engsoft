from django.urls import path

from .views import (
    FoodDetailView,
    FoodListCreateView,
    MealLogCreateView,
)

app_name = "foods"

urlpatterns = [
    path("", FoodListCreateView.as_view(), name="food"),
    path("<int:food_id>/", FoodDetailView.as_view(), name="detail"),
    path("tracker/log/", MealLogCreateView.as_view(), name="meal-log-create"),
]
