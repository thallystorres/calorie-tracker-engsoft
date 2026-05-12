from decimal import Decimal

from django.contrib.auth.models import User
from django.db.models.query import QuerySet

from .models import (
    FoodRestriction,
    NutritionalProfile,
    SavedDiet,
    SavedRecipe,
    WeeklyPlan,
)


class NutritionalProfileRepository:
    def update_targets(
        self, profile: NutritionalProfile, bmr: Decimal, daily_target: Decimal
    ) -> NutritionalProfile:
        profile.bmr = bmr  # type: ignore
        profile.daily_calorie_target = daily_target  # type: ignore

        profile.save(update_fields=["bmr", "daily_calorie_target", "updated_at"])

        return profile

    def get_by_user_id(self, user_id: int) -> NutritionalProfile:
        return NutritionalProfile.objects.get(user__id=user_id)

    def create_diet(self, user: User, title: str, content: str) -> SavedDiet:
        return SavedDiet.objects.create(user=user, title=title, content=content)

    def create_recipe(self, user: User, title: str, content: str) -> SavedRecipe:
        return SavedRecipe.objects.create(user=user, title=title, content=content)

    def create_weekly_plan(
        self, user: User, title: str, plan_data: dict, target_kcal: Decimal | None = None
    ) -> WeeklyPlan:
        return WeeklyPlan.objects.create(
            user=user,
            title=title,
            plan_data=plan_data,
            target_kcal_per_day=target_kcal,
        )

    def list_diets(self, user: User) -> QuerySet[SavedDiet]:
        return SavedDiet.objects.filter(user=user).order_by("-created_at")

    def list_recipes(self, user: User) -> QuerySet[SavedDiet]:
        return SavedRecipe.objects.filter(user=user).order_by("-created_at")

    def list_weekly_plans(self, user: User) -> QuerySet[WeeklyPlan]:
        return WeeklyPlan.objects.filter(user=user).order_by("-id")

    def list_diets_from_id_list(self, user: User, id_list) -> QuerySet[SavedDiet]:
        return SavedDiet.objects.filter(id__in=id_list, user=user).values_list(
            "content", flat=True
        )

    def list_recipes_from_id_list(self, user: User, id_list) -> QuerySet[SavedDiet]:
        SavedRecipe.objects.filter(id__in=id_list, user=user).values_list(
            "content", flat=True
        )


class FoodRestrictionRepository:
    def search_profile(self, profile: NutritionalProfile):
        return FoodRestriction.objects.filter(profile=profile).order_by("id")
