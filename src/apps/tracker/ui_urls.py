from django.urls import path

from . import ui_views

app_name = "tracker-ui"

urlpatterns = [
    path("", ui_views.tracker_page, name="tracker"),
    path("dashboard/", ui_views.tracker_dashboard_partial, name="dashboard"),
    path("history/", ui_views.tracker_history_partial, name="history"),
]
