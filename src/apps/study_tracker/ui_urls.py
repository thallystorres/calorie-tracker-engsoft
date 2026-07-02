from django.urls import path
from . import ui_views

app_name = "study_tracker-ui"

urlpatterns = [
    path("", ui_views.tracker_page, name="tracker"),
    path("dashboard/", ui_views.tracker_dashboard_partial, name="dashboard"),
    path("add-item/", ui_views.add_study_item_partial, name="add-item"),
    path("save-session/", ui_views.save_session, name="save-session"),
]
