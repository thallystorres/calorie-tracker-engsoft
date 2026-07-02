from django.urls import path
from . import ui_views

app_name = "study_ai_engine-ui"

urlpatterns = [
    path("hub/", ui_views.hub_page, name="hub"),
    path("generate/quiz/", ui_views.generate_quiz, name="generate-quiz"),
    path("generate/flashcards/", ui_views.generate_flashcards, name="generate-flashcards"),
]
