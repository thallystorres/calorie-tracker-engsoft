from django.urls import path

from .views import SuggestMealView

app_name = "ai"

urlpatterns = [
    path("suggest_meal/", SuggestMealView.as_view(), name="suggest_meal"),
]
