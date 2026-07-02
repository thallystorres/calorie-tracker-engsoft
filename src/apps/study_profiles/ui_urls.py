from django.urls import path
from . import ui_views

app_name = "study_profiles-ui"

urlpatterns = [
    path("me/", ui_views.profile_page, name="profile"),
    path("me/save/", ui_views.save_profile, name="save-profile"),
]
