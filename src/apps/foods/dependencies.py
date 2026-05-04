from functools import cache

from .repositories import FoodRepository
from .services import FoodService


@cache
def get_food_repository() -> FoodRepository:
    return FoodRepository()


@cache
def get_food_service() -> FoodService:
    return FoodService(food_repository=get_food_repository())
