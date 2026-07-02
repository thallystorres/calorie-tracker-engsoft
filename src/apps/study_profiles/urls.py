from django.urls import path
from . import views

app_name = "study_profiles"

urlpatterns = [
    path("me/", views.StudyProfileView.as_view(), name="me"),
]
