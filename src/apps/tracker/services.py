from typing import TYPE_CHECKING

from django.contrib.auth.models import User
from django.db import transaction

from apps.foods.allergens import (
    normalize_food_allergens,
    normalize_profile_restrictions,
)
from apps.profiles.dependencies import get_profile_service

from .models import Meal
from .repositories import MealRepository

if TYPE_CHECKING:
    from apps.foods.models import Food


class TrackerService:
    def __init__(self, meal_repository: MealRepository):
        self._repo = meal_repository

    def _extract_profile_restrictions(self, user: User) -> set[str]:
        restriction_codes = get_profile_service().extract_user_restriction_codes(user)
        return normalize_profile_restrictions(restriction_codes)

    @transaction.atomic
    def log_meal(self, *, user: User, validated_data: dict) -> tuple[Meal, list[str]]:
        label = validated_data["label"]
        items_data = validated_data["items"]

        warnings_set: set[str] = set()
        restrictions = self._extract_profile_restrictions(user)

        meal = self._repo.create_meal(user=user, label=label)

        for item in items_data:
            food: Food = item["food_id"]
            quantity_grams = item["quantity_grams"]

            if restrictions:
                allergens = set(normalize_food_allergens(food.allergens or []))
                conflicts = restrictions.intersection(allergens)
                if conflicts:
                    conflicts_text = ", ".join(sorted(conflicts)).title()
                    warnings_set.add(
                        f'Atenção: O alimento "{food.name}" possui componentes '
                        f"{conflicts_text} que conflitam com as suas restrições"
                    )

            self._repo.create_meal_item(
                meal=meal, food=food, quantity_grams=quantity_grams
            )

        return meal, sorted(warnings_set)
