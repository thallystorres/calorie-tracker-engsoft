from django.contrib.auth.models import User
from django.db import models


class NutritionalProfile(models.Model):
    class SexChoices(models.TextChoices):
        MALE = "M", "Masculino"
        FEMALE = "F", "Feminino"

    class ActivityLevelChoices(models.TextChoices):
        SEDENTARY = "SEDENTARIO", "Sedentário"
        LIGHT = "LEVE", "Leve"
        MODERATE = "MODERADA", "Moderada"
        HIGH = "ALTA", "Alta"
        VERY_HIGH = "MUITO_ALTA", "Muito Alta"

    class GoalChoices(models.TextChoices):
        LOSE = "PERDA", "Perda"
        MAINTAIN = "MANUTENCAO", "Manuteção"
        GAIN = "GANHO", "Ganho"

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="nutritional_profile"
    )

    weight_kg = models.DecimalField(max_digits=5, decimal_places=2)
    height_cm = models.PositiveIntegerField()
    age = models.PositiveIntegerField()

    sex = models.CharField(max_length=1, choices=SexChoices.choices)
    activity_level = models.CharField(
        max_length=15, choices=ActivityLevelChoices.choices
    )
    goal = models.CharField(max_length=15, choices=GoalChoices.choices)
    bmr = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    daily_calorie_target = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Perfil Nutricional - {self.user.username}" # type: ignore
