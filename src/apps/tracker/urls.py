from django.urls import path

from .views import MealCreateView

app_name = "tracker"

urlpatterns = [path("meals/", MealCreateView.as_view(), name="meal-create")]
