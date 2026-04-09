from django.urls import path

from . import ui_views

app_name = "foods-ui"

urlpatterns = [
    path("tracker/", ui_views.tracker_page, name="tracker"),
]
