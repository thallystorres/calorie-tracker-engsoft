from django.urls import path

from .views import ProfileMeView

app_name = "profiles"

urlpatterns = [
    path("me/", ProfileMeView.as_view(), name="me")
]