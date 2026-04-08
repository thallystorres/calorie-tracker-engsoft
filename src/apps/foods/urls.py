from django.urls import path

from .views import (
    FoodDetailView,
    FoodListCreateView,
)

app_name = "foods"

urlpatterns = [
    path("", FoodListCreateView.as_view(), name="food"),
    path("<int:food_id>/", FoodDetailView.as_view(), name="detail"),
]
