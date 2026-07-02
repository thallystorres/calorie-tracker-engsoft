from django.contrib.auth.models import User
from django.db import models
from apps.contents.models import StudyContent
from core.tracking.models import BaseTrackedEvent, BaseTrackedItem

class StudySession(BaseTrackedEvent):
    class StrategyChoices(models.TextChoices):
        POMODORO = "POMODORO", "Pomodoro"
        FEYNMAN = "FEYNMAN", "Técnica de Feynman"
        ACTIVE_RECALL = "ACTIVE_RECALL", "Active Recall"
        LEITURA = "LEITURA", "Leitura Ativa"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="study_sessions")
    strategy = models.CharField(max_length=20, choices=StrategyChoices.choices)

class StudyItem(BaseTrackedItem):
    session = models.ForeignKey(StudySession, on_delete=models.CASCADE, related_name="items")
    content = models.ForeignKey(StudyContent, on_delete=models.CASCADE)

    time_minutes = models.PositiveIntegerField()
    notes = models.TextField(blank=True)

    def get_metric(self):
        return self.time_minutes
