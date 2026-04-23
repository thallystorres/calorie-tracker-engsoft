from typing import TYPE_CHECKING

from django.contrib.auth.models import User
from django.db import transaction

from apps.foods.allergens import (
    normalize_food_allergens,
    normalize_profile_restrictions,
)
from apps.profiles.restrictions import extract_user_restriction_codes

from .models import Meal, MealItem

if TYPE_CHECKING:
    from apps.foods.models import Food


class TrackerService:
    def _extract_profile_restrictions(self, user: User) -> set[str]:
        restriction_codes = extract_user_restriction_codes(user)
        return normalize_profile_restrictions(restriction_codes)

    @transaction.atomic
    def log_meal(self, *, user: User, validated_data: dict) -> tuple[Meal, list[str]]:
        label = validated_data["label"]
        items_data = validated_data["items"]

        warnings: list[str] = []
        meal = Meal.objects.create(user=user, label=label)

        for item in items_data:
            food: Food = item["food_id"]
            quantity_grams = item["quantity_grams"]

            restrictions = self._extract_profile_restrictions(user)
            if restrictions:
                allergens = set(normalize_food_allergens(food.allergens or []))
                conflicts = restrictions.intersection(allergens)
                if conflicts:
                    conflicts_text = ", ".join(sorted(conflicts)).title()
                    warnings.append(
                        f'Atenção: O alimento "{food.name}" possui componentes '
                        f"{conflicts_text} que conflitam com as suas "
                        f"restrições alimentares"
                    )
            MealItem.objects.create(meal=meal, food=food, quantity_grams=quantity_grams)

        return meal, warnings
