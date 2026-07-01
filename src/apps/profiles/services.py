from decimal import Decimal

from django.contrib.auth.models import User

from apps.smarttracker_fw.profiles.services import BaseProfileService

from .models import FoodRestriction, NutritionalProfile
from .repositories import NutritionalProfileRepository


class ProfileService(BaseProfileService):
    def __init__(self, repository: NutritionalProfileRepository):
        self.repo = repository

    # 1. Implement the Framework Hook
    def calculate_custom_targets(self, profile: NutritionalProfile) -> None:
        # The framework has already set the new weight, height, age, etc.
        # Now we calculate the CalorIA specific targets before it saves.
        profile.bmr = self.calculate_bmr(
            profile.weight_kg, profile.height_cm, profile.age, profile.sex
        )
        profile.daily_calorie_target = self.calculate_daily_target(
            profile.bmr, profile.activity_level, profile.goal
        )

    # 2. Keep the original domain math methods
    def calculate_bmr(
        self, weight: Decimal, height: int, age: int, sex: str
    ) -> Decimal:
        # ... (Your exact same mathematical logic here)
        pass

    def calculate_daily_target(
        self, bmr: Decimal, activity_level: str, goal: str
    ) -> Decimal:
        # ... (Your exact same TDEE multiplier logic here)
        pass

    # 3. Keep the CalorIA-specific restriction logic
    def replace_restrictions(
        self, *, profile: NutritionalProfile, restrictions_data: list[dict]
    ) -> None:
        FoodRestriction.objects.filter(profile=profile).delete()
        new_items = [
            FoodRestriction(profile=profile, **item) for item in restrictions_data
        ]
        if new_items:
            FoodRestriction.objects.bulk_create(new_items)

    def extract_user_restriction_codes(self, user: User) -> set[str]:
        profile = getattr(user, "nutritional_profile", None)
        if profile is None:
            return set()
        return self._extract_profile_restriction_codes(profile)

    def _extract_profile_restriction_codes(
        self, profile: NutritionalProfile
    ) -> set[str]:
        restriction_codes: set[str] = set()

        restriction_items = getattr(profile, "restriction_items", None)
        if restriction_items is not None and hasattr(restriction_items, "values_list"):
            restriction_codes.update(
                value
                for value in restriction_items.values_list(
                    "restriction_type", flat=True
                )
                if value
            )

        return restriction_codes
