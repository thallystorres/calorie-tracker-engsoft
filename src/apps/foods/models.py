from decimal import Decimal

from django.contrib.auth.models import User
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

class MealLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="meal_logs")
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity_g = models.DecimalField(
        max_digits=7, decimal_places=2, validators=[MinValueValidator(Decimal('0.1'))]
    )
    consumed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.user.username} consumiu {self.quantity_g}g de {self.food.name}"
