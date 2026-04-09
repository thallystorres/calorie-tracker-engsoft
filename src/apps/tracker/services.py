from django.contrib.auth.models import User
from django.db import transaction

from apps.foods.models import Food

from .models import Meal, MealItem


class TrackerService:
    @transaction.atomic
    def log_meal(self, *, user: User, validated_data: dict) -> tuple[Meal, list[str]]:
        label = validated_data["label"]
        items_data = validated_data["items"]

        warnings: list[str] = []
        meal = Meal.objects.create(user=user, label=label)

        for item in items_data:
            food: Food = item["food_id"]
            quantity_grams = item["quantity_grams"]

            if hasattr(user, "nutritional_profile"):
                restrictions = set(user.nutritional_profile.dietary_restrictions or [])  # type:ignore
                allergens = set(food.allergens or [])
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
