from django.contrib.auth.models import User
from django.db import models
from core.profiles.models import BaseProfile
from core.tracking.models import BaseAIGeneratedContent

class StudyProfile(BaseProfile):
    class GoalChoices(models.TextChoices):
        CONCURSO = "CONCURSO", "Concurso Público"
        FACULDADE = "FACULDADE", "Ensino Superior / Faculdade"
        IDIOMA = "IDIOMA", "Aprender Idioma"
        PROFISSAO = "PROFISSAO", "Certificação / Profissional"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="study_profile")

    weekly_availability_hours = models.PositiveIntegerField(default=10)
    focus_limit_minutes = models.PositiveIntegerField(
        default=60, help_text="Tempo máximo focado sem pausas (ex: Pomodoro)"
    )
    goal = models.CharField(max_length=20, choices=GoalChoices.choices)

    target_weekly_minutes = models.PositiveIntegerField(null=True, blank=True)
    target_recall_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    target_quiz_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

class SavedSummary(BaseAIGeneratedContent):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_summaries")

class SavedFlashcardSet(BaseAIGeneratedContent):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_flashcards")

class SavedQuiz(BaseAIGeneratedContent):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_quizzes")
