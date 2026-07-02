from django.contrib.auth.models import User
from django.db import models

from core.profiles.models import BaseProfile
from core.tracking.models import (
    BaseAIGeneratedContent,
    BaseCatalogItem,
    BaseGoal,
    BaseTrackedEvent,
    BaseTrackedItem,
)


class Exercise(BaseCatalogItem):
    class MuscleGroupsChoices(models.TextChoices):
        CHEST = "chest", "Peitoral"
        BACK = "back", "Costas"
        QUADS = "quads", "Quadriceps"
        HAMSTRINGS = "hamstrings", "Posteriores"
        SHOULDERS = "shoulders", "Ombros"
        BICEPS = "biceps", "Bíceps"
        TRICEPS = "triceps", "Tríceps"
        GLUTES = "glutes", "Glúteos"
        CALVES = "calves", "Panturrilhas"
        ABS = "abs", "Abdômen"

    muscle_group = models.CharField(max_length=50, choices=MuscleGroupsChoices.choices)
    description = models.TextField()


class WorkoutSession(BaseTrackedEvent):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    duration_minutes = models.PositiveIntegerField(null=True)

    @property
    def total_volume(self):
        return sum(s.get_metric() for s in self.sets.all())


class WorkoutSet(BaseTrackedItem):
    session = models.ForeignKey(
        WorkoutSession, related_name="sets", on_delete=models.CASCADE
    )
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    reps = models.PositiveIntegerField()
    weight = models.FloatField(help_text="Peso em Kg")

    def get_metric(self):
        return self.reps * self.weight


class FitnessProfile(BaseProfile):
    class ExperienceLevelChoices(models.TextChoices):
        BEGINNER = "beginner", "Iniciante"
        INTERMEDIARY = "intermediary", "Intermediário"
        ADVANCED = "advanced", "Avançado"

    class PrimaryGoalChoices(models.TextChoices):
        HYPERTROPHY = "hypertrophy", "Hipertrofia"
        POWERLIFT = "powerlift", "Força"
        WEIGHT_LOSS = "weight_loss", "Perda de Peso"

    experience_level = models.CharField(
        max_length=20, choices=ExperienceLevelChoices.choices
    )
    primary_goal = models.CharField(max_length=50, choices=PrimaryGoalChoices.choices)


class MuscleVolumeGoal(BaseGoal):
    muscle_group = models.CharField(
        max_length=50, choices=Exercise.MuscleGroupsChoices.choices
    )


class AIWorkoutRoutine(BaseAIGeneratedContent):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan_data = models.JSONField()
