from decimal import Decimal

from .models import NutritionalProfile


class NutritionalProfileRepository:
    @staticmethod
    def update_targets(
        profile: NutritionalProfile, bmr: Decimal, daily_target: Decimal
    ) -> NutritionalProfile:
        profile.bmr = bmr  # type: ignore
        profile.daily_calorie_target = daily_target  # type: ignore

        profile.save(update_fields=["bmr", "daily_calorie_target", "updated_at"])

        return profile
