from decimal import ROUND_HALF_UP, Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Food(models.Model):
    class FoodSource(models.TextChoices):
        USDA = "usda", "US Departament of Agriculture"
        MANUAL = "manual", "Manual"
        OFF = "off", "Open Food Facts"

    name = models.CharField(max_length=255, db_index=True)
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
    source = models.CharField(max_length=10, choices=FoodSource.choices)
    outsource_fdc_id = models.IntegerField(null=True, blank=True)

    allergens = models.JSONField(default=list, blank=True)

    @staticmethod
    def calculate_kcal_per_100g(
        *, protein_per_100g: Decimal, carbs_per_100g: Decimal, fat_per_100g: Decimal
    ) -> Decimal:
        kcal = (
            (Decimal("4") * protein_per_100g)
            + (Decimal("4") * carbs_per_100g)
            + (Decimal("9") * fat_per_100g)
        )
        return kcal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _set_missing_kcal(self) -> None:
        if self.kcal_per_100g is not None:
            return

        if (
            self.protein_per_100g is None
            or self.carbs_per_100g is None
            or self.fat_per_100g is None
        ):
            raise ValidationError(
                {
                    "kcal_per_100g": (
                        "Para calcular kcal automaticamente, protein_per_100g, "
                        "carbs_per_100g e fat_per_100g são obrigatórios."
                    )
                }
            )

        self.kcal_per_100g = self.calculate_kcal_per_100g(
            protein_per_100g=self.protein_per_100g,
            carbs_per_100g=self.carbs_per_100g,
            fat_per_100g=self.fat_per_100g,
        )

    def save(self, *args, **kwargs):
        self._set_missing_kcal()
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name
