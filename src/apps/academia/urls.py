from django.urls import path

from .views import WorkoutListCreateView

app_name = "academia"

urlpatterns = [
    path("workouts/", WorkoutListCreateView.as_view(), name="workout-list-create"),
]
