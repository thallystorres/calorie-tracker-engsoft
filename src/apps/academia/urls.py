from django.urls import path

from .views import (
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
]
