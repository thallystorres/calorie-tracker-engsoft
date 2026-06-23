from decimal import ROUND_HALF_UP, Decimal
from django.core.exceptions import ValidationError
from django.db import models
from pgvector.django import VectorField
from core.base_models import BaseTrackableEntity

class Food(BaseTrackableEntity):
    class FoodSource(models.TextChoices):
        USDA = "usda", "US Departament of Agriculture"
        MANUAL = "manual", "Manual"
        OFF = "off", "Open Food Facts"

    source = models.CharField(max_length=10, choices=FoodSource.choices)
    outsource_fdc_id = models.IntegerField(null=True, blank=True)
    allergens = models.JSONField(default=list, blank=True)
    embedding = VectorField(dimensions=3072, null=True, blank=True)

    # --- Hot Spot: Métricas do CalorIA mapeadas para base_metrics ---
    @property
    def kcal_per_100g(self): return Decimal(str(self.base_metrics.get("kcal_per_100g", 0)))
    @kcal_per_100g.setter
    def kcal_per_100g(self, value): self.base_metrics["kcal_per_100g"] = str(value)

    @property
    def protein_per_100g(self): return Decimal(str(self.base_metrics.get("protein_per_100g", 0)))
    @protein_per_100g.setter
    def protein_per_100g(self, value): self.base_metrics["protein_per_100g"] = str(value)

    @property
    def carbs_per_100g(self): return Decimal(str(self.base_metrics.get("carbs_per_100g", 0)))
    @carbs_per_100g.setter
    def carbs_per_100g(self, value): self.base_metrics["carbs_per_100g"] = str(value)

    @property
    def fat_per_100g(self): return Decimal(str(self.base_metrics.get("fat_per_100g", 0)))
    @fat_per_100g.setter
    def fat_per_100g(self, value): self.base_metrics["fat_per_100g"] = str(value)

    @property
    def fiber_per_100g(self): return Decimal(str(self.base_metrics.get("fiber_per_100g", 0)))
    @fiber_per_100g.setter
    def fiber_per_100g(self, value): self.base_metrics["fiber_per_100g"] = str(value)

    @staticmethod
    def calculate_kcal_per_100g(*, protein_per_100g: Decimal, carbs_per_100g: Decimal, fat_per_100g: Decimal) -> Decimal:
        kcal = ((Decimal("4") * protein_per_100g) + (Decimal("4") * carbs_per_100g) + (Decimal("9") * fat_per_100g))
        return kcal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _set_missing_kcal(self) -> None:
        if self.base_metrics.get("kcal_per_100g"):
            return

        if not all([self.base_metrics.get("protein_per_100g"), self.base_metrics.get("carbs_per_100g"), self.base_metrics.get("fat_per_100g")]):
            raise ValidationError({"kcal_per_100g": "Para calcular kcal automaticamente, protein, carbs e fat são obrigatórios."})

        self.kcal_per_100g = self.calculate_kcal_per_100g(
            protein_per_100g=self.protein_per_100g,
            carbs_per_100g=self.carbs_per_100g,
            fat_per_100g=self.fat_per_100g,
        )

    def save(self, *args, **kwargs):
        self._set_missing_kcal()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name
