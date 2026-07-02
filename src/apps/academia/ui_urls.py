from django.urls import path

from . import ui_views

app_name = "academia-ui"

urlpatterns = [
    path("", ui_views.academia_page, name="academia"),
    path("dashboard/", ui_views.volume_dashboard_partial, name="dashboard"),
    path("history/", ui_views.workout_history_partial, name="history"),
    path("goals/", ui_views.goals_partial, name="goals"),
]
