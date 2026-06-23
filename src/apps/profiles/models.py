from decimal import Decimal
from django.db import models
from core.base_models import BaseProfile
from django.contrib.auth.models import User

class NutritionalProfile(BaseProfile):
    class SexChoices(models.TextChoices):
        MALE = "M", "Masculino"
        FEMALE = "F", "Feminino"

    class ActivityLevelChoices(models.TextChoices):
        SEDENTARY = "SEDENTARIO", "Sedentário"
        LEVE = "LEVE", "Leve"
        MODERATE = "MODERADA", "Moderada"
        HIGH = "ALTA", "Alta"
        VERY_HIGH = "MUITO_ALTA", "Muito Alta"

    class GoalChoices(models.TextChoices):
        LOSE = "PERDA", "Perda"
        MAINTAIN = "MANUTENCAO", "Manuteção"
        GAIN = "GANHO", "Ganho"

    dietary_restrictions = models.JSONField(default=list, blank=True)

    # --- Hot Spot: Propriedades mapeadas para o JSONField metrics_data ---
    @property
    def weight_kg(self): return Decimal(str(self.metrics_data.get("weight_kg", 0)))
    @weight_kg.setter
    def weight_kg(self, value): self.metrics_data["weight_kg"] = str(value)

    @property
    def height_cm(self): return int(self.metrics_data.get("height_cm", 0))
    @height_cm.setter
    def height_cm(self, value): self.metrics_data["height_cm"] = int(value)

    @property
    def age(self): return int(self.metrics_data.get("age", 0))
    @age.setter
    def age(self, value): self.metrics_data["age"] = int(value)

    @property
    def sex(self): return self.metrics_data.get("sex", "")
    @sex.setter
    def sex(self, value): self.metrics_data["sex"] = str(value)

    @property
    def activity_level(self): return self.metrics_data.get("activity_level", "")
    @activity_level.setter
    def activity_level(self, value): self.metrics_data["activity_level"] = str(value)

    @property
    def goal(self): return self.metrics_data.get("goal", "")
    @goal.setter
    def goal(self, value): self.metrics_data["goal"] = str(value)

    @property
    def bmr(self): return Decimal(str(self.metrics_data.get("bmr", 0))) if self.metrics_data.get("bmr") else None
    @bmr.setter
    def bmr(self, value): self.metrics_data["bmr"] = str(value) if value else None

    @property
    def daily_calorie_target(self): return Decimal(str(self.metrics_data.get("daily_calorie_target", 0))) if self.metrics_data.get("daily_calorie_target") else None
    @daily_calorie_target.setter
    def daily_calorie_target(self, value): self.metrics_data["daily_calorie_target"] = str(value) if value else None

    @property
    def remind_interval_hours(self): return int(self.metrics_data.get("remind_interval_hours", 3))
    @remind_interval_hours.setter
    def remind_interval_hours(self, value): self.metrics_data["remind_interval_hours"] = int(value)

    def __str__(self) -> str:
        return f"Perfil Nutricional - {self.user.username}"

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


class WeeklyPlan(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="weekly_plans"
    )
    title = models.CharField(max_length=255, default="Meu Plano Semanal")

    is_active = models.BooleanField(
        default=False, help_text="É o plano que o usuário está seguindo agora?"
    )
    start_date = models.DateField(null=True, blank=True)
    target_kcal_per_day = models.DecimalField(max_digits=7, decimal_places=2, null=True)

    plan_data = models.JSONField(
        help_text="JSON estruturado contendo os dias, refeições e ingredientes"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
