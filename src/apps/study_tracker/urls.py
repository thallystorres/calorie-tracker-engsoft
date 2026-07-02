from django.urls import path
from . import views

app_name = "study_tracker"

urlpatterns = [
    path("sessions/", views.StudySessionCreateView.as_view(), name="session-create"),
]
