from django.contrib.auth.models import User
from django.db import models
from core.profiles.models import BaseProfile
from core.tracking.models import BaseAIGeneratedContent


class NutritionalProfile(BaseProfile):
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

    dietary_restrictions = models.JSONField(default=list, blank=True)
    sex = models.CharField(max_length=1, choices=SexChoices.choices)
    activity_level = models.CharField(
        max_length=15, choices=ActivityLevelChoices.choices
    )
    goal = models.CharField(max_length=15, choices=GoalChoices.choices)
    bmr = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    daily_calorie_target = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True
    )


class FoodRestriction(models.Model):
    class RestrictionTypeChoices(models.TextChoices):
        GLUTEN_FREE = "CELIACO", "Celíaco"
        LACTOSE_INTOLERANT = "INTOLERANTE_A_LACTOSE", "Intolerante à Lactose"
        DIABETIC = "DIABETICO", "Diabético"
        EGGS = "ALERGICO_OVO", "Alérgico a ovo"
        SEAFOOD = "FRUTOS_DO_MAR", "Alérgico a frutos do mar"
        PEANUTS = "AMENDOIM", "Alérgico a amendoim"
        SOY = "SOJA", "Alérgico à soja"
        OATS = "AVEIA", "Alérgico à aveia"
        OTHER = "OUTRO", "Outro"

    profile = models.ForeignKey(
        NutritionalProfile, on_delete=models.CASCADE, related_name="restriction_items"
    )
    restriction_type = models.CharField(
        max_length=30, choices=RestrictionTypeChoices.choices
    )
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        if self.restriction_type == self.RestrictionTypeChoices.OTHER:
            return f"{self.profile} - {self.description}"
        return f"{self.profile} - {self.get_restriction_type_display()}"


class SavedDiet(BaseAIGeneratedContent):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_diets")
    title = models.CharField(max_length=255, default="Plano Alimentar Inteligente")


class SavedRecipe(BaseAIGeneratedContent):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="saved_recipes"
    )
    title = models.CharField(max_length=255, default="Receita Saudável")


class WeeklyPlan(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="weekly_plans"
    )
    title = models.CharField(max_length=255, default="Meu Plano Semanal")
    is_active = models.BooleanField(default=False)
    start_date = models.DateField(null=True, blank=True)
    target_kcal_per_day = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    plan_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
