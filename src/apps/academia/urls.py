from django.urls import path

from .views import (
    ExerciseListView,
    GenerateRoutineView,
    GoalsListView,
    GoalsRecalculateView,
    VolumeMetricsView,
    WeeklyVolumeMetricsView,
    WorkoutListCreateView,
)

app_name = "academia"

urlpatterns = [
    path("workouts/", WorkoutListCreateView.as_view(), name="workout-list-create"),
    path("metrics/volume/", VolumeMetricsView.as_view(), name="volume-metrics"),
    path(
        "metrics/volume/weekly/",
        WeeklyVolumeMetricsView.as_view(),
        name="weekly-volume-metrics",
    ),
    path("goals/", GoalsListView.as_view(), name="goals-list"),
    path("goals/recalculate/", GoalsRecalculateView.as_view(), name="goals-recalculate"),
    path("ai/generate-routine/", GenerateRoutineView.as_view(), name="generate-routine"),
    path("exercises/", ExerciseListView.as_view(), name="exercise-list"),
]
