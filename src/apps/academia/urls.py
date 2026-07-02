from django.urls import path

from .views import (
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
]
