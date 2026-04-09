from django.urls import path

from . import ui_views

app_name = "profiles-ui"

urlpatterns = [
    path(
        "nutritional-profile/",
        ui_views.nutritional_profile_page,
        name="nutritional-profile",
    ),
]
