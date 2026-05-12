from django.urls import path

from .views import (
    FoodDetailView,
    FoodListCreateView,
    FoodSearchView,
)

app_name = "foods"

urlpatterns = [
    path("", FoodListCreateView.as_view(), name="food"),
    path("search/", FoodSearchView.as_view(), name="search"),
    path("<int:food_id>/", FoodDetailView.as_view(), name="detail"),
]
