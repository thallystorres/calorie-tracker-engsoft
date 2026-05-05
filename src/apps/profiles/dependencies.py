from functools import cache

from .repositories import FoodRestrictionRepository, NutritionalProfileRepository
from .services import ProfileService


@cache
def get_profile_repository() -> NutritionalProfileRepository:
    return NutritionalProfileRepository()


@cache
def get_profile_service() -> ProfileService:
    return ProfileService(repository=get_profile_repository())


@cache
def get_food_restriction_repository() -> FoodRestrictionRepository:
    return FoodRestrictionRepository()
