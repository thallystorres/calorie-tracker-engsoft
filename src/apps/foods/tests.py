from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError as DjangoValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

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


class FoodApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="foods_user",
            email="foods@example.com",
            password="Forte@1234",
        )
        self.list_url = reverse("foods:food")

        self.valid_payload = {
            "name": "Arroz branco cozido",
            "kcal_per_100g": "130.00",
            "protein_per_100g": "2.50",
            "carbs_per_100g": "28.00",
            "fat_per_100g": "0.30",
            "fiber_per_100g": "0.40",
        }

    def authenticate(self) -> None:
        self.client.force_login(self.user)

    def test_list_requires_authentication(self) -> None:
        response = self.client.get(self.list_url)
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_post_creates_food_with_manual_source(self) -> None:
        self.authenticate()

        response = self.client.post(
            self.list_url, data=self.valid_payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["source"], Food.FoodSource.MANUAL)
        self.assertEqual(Food.objects.count(), 1)

    def test_post_calculates_kcal_when_missing(self) -> None:
        self.authenticate()
        payload = {
            "name": "Frango grelhado",
            "protein_per_100g": "31.00",
            "carbs_per_100g": "0.00",
            "fat_per_100g": "3.60",
            "fiber_per_100g": "0.00",
        }

        response = self.client.post(self.list_url, data=payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["kcal_per_100g"], "156.40")

    def test_post_keeps_kcal_when_provided(self) -> None:
        self.authenticate()
        payload = {
            "name": "Aveia",
            "kcal_per_100g": "370.00",
            "protein_per_100g": "13.00",
            "carbs_per_100g": "60.00",
            "fat_per_100g": "7.00",
            "fiber_per_100g": "10.00",
        }

        response = self.client.post(self.list_url, data=payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["kcal_per_100g"], "370.00")

    def test_post_rejects_duplicate_name_case_insensitive(self) -> None:
        self.authenticate()
        Food.objects.create(
            name="Banana",
            kcal_per_100g="89.00",
            protein_per_100g="1.10",
            carbs_per_100g="22.80",
            fat_per_100g="0.30",
            fiber_per_100g="2.60",
            source=Food.FoodSource.MANUAL,
        )

        payload = {
            "name": "banana",
            "kcal_per_100g": "88.00",
            "protein_per_100g": "1.00",
            "carbs_per_100g": "22.00",
            "fat_per_100g": "0.20",
            "fiber_per_100g": "2.50",
        }
        response = self.client.post(self.list_url, data=payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("já existe", str(response.data))

    def test_list_filters_by_query_q(self) -> None:
        self.authenticate()
        Food.objects.create(
            name="Arroz integral",
            kcal_per_100g="124.00",
            protein_per_100g="2.60",
            carbs_per_100g="25.00",
            fat_per_100g="1.00",
            fiber_per_100g="1.80",
            source=Food.FoodSource.MANUAL,
        )
        Food.objects.create(
            name="Frango grelhado",
            kcal_per_100g="165.00",
            protein_per_100g="31.00",
            carbs_per_100g="0.00",
            fat_per_100g="3.60",
            fiber_per_100g="0.00",
            source=Food.FoodSource.MANUAL,
        )

        response = self.client.get(self.list_url, data={"q": "arroz"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "Arroz integral")

    def test_list_is_paginated_with_20_items(self) -> None:
        self.authenticate()
        for i in range(25):
            Food.objects.create(
                name=f"Food {i}",
                kcal_per_100g="100.00",
                protein_per_100g="10.00",
                carbs_per_100g="10.00",
                fat_per_100g="2.00",
                fiber_per_100g="1.00",
                source=Food.FoodSource.MANUAL,
            )

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 25)
        self.assertEqual(len(response.data["results"]), 20)

    def test_detail_returns_food(self) -> None:
        self.authenticate()
        food = Food.objects.create(
            name="Iogurte natural",
            kcal_per_100g="61.00",
            protein_per_100g="3.50",
            carbs_per_100g="4.70",
            fat_per_100g="3.30",
            fiber_per_100g="0.00",
            source=Food.FoodSource.MANUAL,
        )
        detail_url = reverse("foods:detail", kwargs={"food_id": food.id})

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], food.id)

    def test_detail_returns_404_for_missing_food(self) -> None:
        self.authenticate()
        detail_url = reverse("foods:detail", kwargs={"food_id": 999999})

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
