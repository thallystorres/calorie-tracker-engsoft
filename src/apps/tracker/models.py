from decimal import ROUND_HALF_UP, Decimal
from django.db import models
from apps.foods.models import Food
from core.base_models import BaseTrackingSession, BaseTrackedItem

class Meal(BaseTrackingSession):
    class MealLabel(models.TextChoices):
        CAFE = "cafe", "Café da Manhã"
        ALMOCO = "almoco", "Almoço"
        JANTAR = "jantar", "Jantar"
        LANCHE = "lanche", "Lanche"
        OUTRO = "outro", "Outro"

    label = models.CharField(max_length=20, choices=MealLabel.choices)

    # Preserva retrocompatibilidade
    @property
    def eaten_at(self): return self.timestamp

    def __str__(self):
        return f"{self.user.username} - {self.label} - {self.timestamp}"


class MealItem(BaseTrackedItem):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name="items")
    food = models.ForeignKey(Food, on_delete=models.CASCADE)

    # --- Hot Spot: Propriedades mapeadas ---
    @property
    def quantity_grams(self): return self.quantity
    @quantity_grams.setter
    def quantity_grams(self, value): self.quantity = value

    @property
    def kcal_total(self): return Decimal(str(self.computed_metrics.get("kcal_total", 0)))
    @kcal_total.setter
    def kcal_total(self, value): self.computed_metrics["kcal_total"] = str(value)

    def save(self, *args, **kwargs):
        kcal = (Decimal(str(self.quantity)) / Decimal("100")) * self.food.kcal_per_100g
        self.kcal_total = kcal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.food.name} ({self.quantity}g)"
