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
    remind_interval_hours = models.PositiveSmallIntegerField(default=3)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Perfil Nutricional - {self.user.username}"  # type: ignore


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

    # Added related_name for easier reverse lookups
    profile = models.ForeignKey(
        NutritionalProfile, on_delete=models.CASCADE, related_name="restriction_items"
    )
    restriction_type = models.CharField(
        max_length=30, choices=RestrictionTypeChoices.choices
    )
    # Bumped to 255 just to be safe, but 100 works too
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        if self.restriction_type == self.RestrictionTypeChoices.OTHER:
            return f"{self.profile} - {self.description}"
        return f"{self.profile} - {self.get_restriction_type_display()}"


class SavedDiet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_diets")
    title = models.CharField(max_length=255, default="Plano Alimentar Inteligente")
    content = models.TextField(help_text="Conteúdo em Markdown gerado pela IA")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"


class SavedRecipe(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="saved_recipes"
    )
    title = models.CharField(max_length=255, default="Receita Saudável")
    content = models.TextField(help_text="Conteúdo em Markdown gerado pela IA")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"
