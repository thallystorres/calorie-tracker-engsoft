from django.contrib.auth.models import User

from apps.foods.allergens import (
    normalize_food_allergens,
    normalize_profile_restrictions,
)
from apps.profiles.dependencies import get_profile_service
from apps.smarttracker_fw.tracking.services import BaseTrackerService

from .repositories import MealRepository


class TrackerService(BaseTrackerService):
    def __init__(self, meal_repository: MealRepository):
        super().__init__(repository=meal_repository)

    def log_meal(self, *, user: User, validated_data: dict):
        event_data = {"label": validated_data["label"]}
        items_data = validated_data["items"]

        return self.log_event(user=user, event_data=event_data, items_data=items_data)

    def validate_event_against_profile(
        self, user: User, items_data: list[dict]
    ) -> list[str]:
        warnings_set: set[str] = set()
        restrictions = self._extract_profile_restrictions(user)

        if not restrictions:
            return []

        for item in items_data:
            food = item["food_id"]
            allergens = set(normalize_food_allergens(food.allergens or []))
            conflicts = restrictions.intersection(allergens)

            if conflicts:
                conflicts_text = ", ".join(sorted(conflicts)).title()
                warnings_set.add(
                    f'Atenção: O alimento "{food.name}" possui componentes '
                    f"{conflicts_text} que conflitam com as suas restrições"
                )

        return sorted(warnings_set)

    def _extract_profile_restrictions(self, user: User) -> set[str]:
        restriction_codes = get_profile_service().extract_user_restriction_codes(user)
        return normalize_profile_restrictions(restriction_codes)
