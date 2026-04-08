from decimal import Decimal

from django.core.exceptions import ValidationError as DjangoValidationError
from django.test import TestCase

from apps.foods.models import Food


class FoodModelTests(TestCase):
    def setUp(self) -> None:
        self.valid_payload = {
            "name": "Arroz branco cozido",
            "kcal_per_100g": Decimal("130.00"),
            "protein_per_100g": Decimal("2.50"),
            "carbs_per_100g": Decimal("28.00"),
            "fat_per_100g": Decimal("0.30"),
            "fiber_per_100g": Decimal("0.40"),
            "source": Food.FoodSource.MANUAL,
            "outsource_fdc_id": None,
        }

    def test_create_manual_food(self) -> None:
        food = Food.objects.create(**self.valid_payload)

        self.assertIsNotNone(food.id)
        self.assertEqual(food.source, Food.FoodSource.MANUAL)
        self.assertIsNone(food.outsource_fdc_id)

    def test_create_usda_food(self) -> None:
        payload = {
            **self.valid_payload,
            "name": "Banana",
            "protein_per_100g": Decimal("1.10"),
            "carbs_per_100g": Decimal("22.80"),
            "fiber_per_100g": Decimal("2.60"),
            "source": Food.FoodSource.USDA,
            "outsource_fdc_id": 173944,
        }

        food = Food.objects.create(**payload)

        self.assertIsNotNone(food.id)
        self.assertEqual(food.source, Food.FoodSource.USDA)
        self.assertEqual(food.outsource_fdc_id, 173944)

    def test_str_returns_name(self) -> None:
        food = Food.objects.create(**self.valid_payload)

        self.assertEqual(str(food), "Arroz branco cozido")

    def test_negative_values_raise_validation_error(self) -> None:
        food = Food(
            **{
                **self.valid_payload,
                "name": "Invalido",
                "kcal_per_100g": Decimal("-1.00"),
            }
        )

        with self.assertRaises(DjangoValidationError):
            food.full_clean()

    def test_name_and_source_are_required(self) -> None:
        food = Food(
            **{
                **self.valid_payload,
                "name": "",
                "source": "",
            }
        )

        with self.assertRaises(DjangoValidationError):
            food.full_clean()

    def test_name_field_has_db_index(self) -> None:
        name_field = Food._meta.get_field("name")

        self.assertTrue(name_field.db_index)
