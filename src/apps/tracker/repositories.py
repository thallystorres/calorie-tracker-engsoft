# type: ignore
from django.contrib.auth.models import User
from django.db.models import DecimalField, ExpressionWrapper, F, QuerySet, Sum
from django.db.models.functions import TruncDate

from core.tracking.repositories import BaseTrackerRepository

from .models import Meal, MealItem

MACROS = {
    "fat": "food__fat_per_100g",
    "carbs": "food__carbs_per_100g",
    "protein": "food__protein_per_100g",
    "fiber": "food__fiber_per_100g",
}


class MealRepository(BaseTrackerRepository[Meal, MealItem]):
    def __init__(self):
        super().__init__(event_model=Meal, item_model=MealItem)

    def create_items(self, event: Meal, items_data: list[dict]) -> list[MealItem]:
        items = [
            self.item_model(
                meal=event, food=data["food_id"], quantity_grams=data["quantity_grams"]
            )
            for data in items_data
        ]
        for item in items:
            item.save()
        return items

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

    def count_days_with_meal_from_date(self, user: User, start_date) -> int:
        meals = Meal.objects.filter(user=user, eaten_at__date__gte=start_date)
        return (
            meals.annotate(data_consumo=TruncDate("eaten_at"))
            .values("data_consumo")
            .distinct()
            .count()
        )

    @property
    def _macro_factor(self) -> ExpressionWrapper:
        return ExpressionWrapper(
            F("quantity_grams") / 100,
            output_field=DecimalField(max_digits=7, decimal_places=4),
        )

    def _macro_sum(self, macro_field: str) -> ExpressionWrapper:
        return ExpressionWrapper(
            self._macro_factor * F(macro_field),
            output_field=DecimalField(max_digits=10, decimal_places=2),
        )

    @property
    def _macro_sums(self) -> dict:
        return {name: Sum(self._macro_sum(field)) for name, field in MACROS.items()}

    def get_daily_totals(self, user: User, date) -> dict:
        qs = MealItem.objects.filter(meal__user=user, meal__eaten_at__date=date)

        return qs.aggregate(kcal=Sum("kcal_total"), **self._macro_sums)

    def get_period_daily_totals(self, *, user: User, start_date, end_date) -> QuerySet:
        qs = MealItem.objects.filter(
            meal__user=user,
            meal__eaten_at__date__gte=start_date,
            meal__eaten_at__date__lte=end_date,
        )

        return (
            qs.annotate(day=TruncDate("meal__eaten_at"))
            .values("day")
            .annotate(kcal=Sum("kcal_total"), **self._macro_sums)
            .order_by("-day")
        )
