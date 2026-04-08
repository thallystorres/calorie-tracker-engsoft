from typing import Any

from rest_framework.exceptions import NotFound, ValidationError

from .models import Food, MealLog
from django.contrib.auth.models import User
from .repositories import FoodRepository


class FoodService:
    def __init__(self, food_repository: FoodRepository):
        self._repo = food_repository

    def list_foods(self, *, query: str | None = None):
        return self._repo.list_foods(query=query)

    def get_food_or_404(self, *, food_id: int) -> Food:
        food = self._repo.get_by_id(food_id=food_id)
        if food is None:
            raise NotFound("Alimento não encontrado.")
        return food

    def create_food(self, *, validated_data: dict[str, Any]) -> Food:
        validated_data["source"] = Food.FoodSource.MANUAL
        if self._repo.exists_by_name(validated_data["name"]):
            raise ValidationError("Alimento com esse nome já existe.")
        return self._repo.create_food(validated_data=validated_data)


class TrackerService:
  def log_meal(self, *, user: User, validated_data: dict[str, Any]) -> tuple[MealLog, list[str]]:
    food: Food = validated_data["food"]
    quantity_g = validated_data["quantity_g"]

    warnings = []

    if hasattr(user, 'nutritional_profile'):
      user_restrictions = set(user.nutritional_profile.dietary_restrictions or [])
      food_allergens = set(food.allergens or [])

      conflitos = user_restrictions.intersection(food_allergens)

      if conflitos:
        itens_conflitantes = ", ".join(conflitos).title()
        warnings.append(
          f"Atenção: O alimento '{food.name}' possui componentes "
          f"({itens_conflitantes}) que conflitam com as suas restrições alimentares."
        )

    meal_log = MealLog.objects.create(
      user=user,
      food=food,
      quantity_g=quantity_g
    )

    return meal_log, warnings
