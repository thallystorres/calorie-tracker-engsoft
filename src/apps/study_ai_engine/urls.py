from django.urls import path
from . import views

app_name = "study_ai_engine"

urlpatterns = [
    path("generate/quiz/", views.GenerateQuizAPIView.as_view(), name="generate-quiz"),
    path("generate/flashcards/", views.GenerateFlashcardsAPIView.as_view(), name="generate-flashcards"),
]
