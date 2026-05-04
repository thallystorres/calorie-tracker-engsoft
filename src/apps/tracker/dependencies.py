from functools import cache

from .repositories import MealRepository
from .services import TrackerService


@cache
def get_meal_repository() -> MealRepository:
    return MealRepository()


@cache
def get_tracker_service() -> TrackerService:
    return TrackerService(meal_repository=get_meal_repository())
