from django.contrib.auth.models import User
from django.db.models import QuerySet

from .models import Meal, MealItem


class MealRepository:
    def create_meal(self, *, user: User, label: str) -> Meal:
        return Meal.objects.create(user=user, label=label)

    def create_meal_item(self, *, meal: Meal, food, quantity_grams) -> MealItem:
        return MealItem.objects.create(
            meal=meal, food=food, quantity_grams=quantity_grams
        )

    def get_meals_for_user(self, *, user: User) -> QuerySet[Meal]:
        return (
            Meal.objects.filter(user=user)
            .prefetch_related("items__food")
            .order_by("-eaten_at")
        )

    def get_meal_items_for_user_from_date(
        self, user: User, start_date
    ) -> QuerySet[MealItem]:
        return MealItem.objects.filter(meal__user=user, meal__eaten_at__gte=start_date)
