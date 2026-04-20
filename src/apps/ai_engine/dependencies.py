from functools import cache

from .services.context_builder import ContextBuilderService
from .services.meal_suggester import MealSuggesterService
from .services.shopping_list import ShoppingListService


@cache
def get_meal_suggester_service() -> MealSuggesterService:
    return MealSuggesterService()


@cache
def get_context_builder_service() -> ContextBuilderService:
    return ContextBuilderService()


@cache
def get_shopping_list_service() -> ShoppingListService:
    return ShoppingListService()
