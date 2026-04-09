from django.urls import path

from . import ui_views

app_name = "tracker-ui"

urlpatterns = [
    path("", ui_views.tracker_page, name="tracker"),
]
