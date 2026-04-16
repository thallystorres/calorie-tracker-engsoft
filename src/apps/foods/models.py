from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Food(models.Model):
    class FoodSource(models.TextChoices):
        USDA = "usda", "US Departament of Agriculture"
        MANUAL = "manual", "Manual"
        OFF = "off", "Open Food Facts"

    name = models.CharField(max_length=255, db_index=True)
    kcal_per_100g = models.DecimalField(
        max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal(0))]
    )
    protein_per_100g = models.DecimalField(
        max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal(0))]
    )
    carbs_per_100g = models.DecimalField(
        max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal(0))]
    )
    fat_per_100g = models.DecimalField(
        max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal(0))]
    )
    fiber_per_100g = models.DecimalField(
        max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal(0))]
    )
    source = models.CharField(max_length=10, choices=FoodSource.choices)
    outsource_fdc_id = models.IntegerField(null=True, blank=True)

    allergens = models.JSONField(default=list, blank=True)

    def __str__(self) -> str:
        return self.name
