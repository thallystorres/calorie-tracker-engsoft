from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from core.tracking.models import BaseCatalogItem

class Food(BaseCatalogItem):
    class FoodSource(models.TextChoices):
        USDA = "usda", "US Departament of Agriculture"
        MANUAL = "manual", "Manual"
        OFF = "off", "Open Food Facts"

    source = models.CharField(max_length=10, choices=FoodSource.choices)
    outsource_fdc_id = models.IntegerField(null=True, blank=True)

    kcal_per_100g = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal(0))],
        blank=True,
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
    allergens = models.JSONField(default=list, blank=True)
