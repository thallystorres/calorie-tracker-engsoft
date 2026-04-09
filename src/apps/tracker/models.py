from decimal import ROUND_HALF_UP, Decimal

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models

from apps.foods.models import Food

# Create your models here.


class Meal(models.Model):
    class MealLabel(models.TextChoices):
        CAFE = "cafe", "Café da Manhã"
        ALMOCO = "almoco", "Almoço"
        JANTAR = "jantar", "Jantar"
        LANCHE = "lanche", "Lanche"
        OUTRO = "outro", "Outro"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="meals")
    label = models.CharField(max_length=20, choices=MealLabel.choices)
    eaten_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.label} - {self.eaten_at}"


class MealItem(models.Model):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name="items")
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity_grams = models.DecimalField(
        max_digits=7, decimal_places=2, validators=[MinValueValidator(Decimal("0.1"))]
    )
    kcal_total = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        default=Decimal("0"),
    )

    def save(self, *args, **kwargs):
        kcal = (self.quantity_grams / Decimal("100")) * self.food.kcal_per_100g
        self.kcal_total = kcal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.food.name} ({self.quantity_grams}g)"
