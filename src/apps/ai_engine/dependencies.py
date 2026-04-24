from functools import cache

from src.apps.ai_engine.services.diet_assistant import DietAssistantService

from .clients.gemini import GeminiLLMClient
from .services.context_builder import ContextBuilder
from .services.meal_suggester import MealSuggesterService


@cache
def get_diet_assistant_service() -> DietAssistantService:
    return DietAssistantService(GeminiLLMClient())


@cache
def get_meal_suggester_service() -> MealSuggesterService:
    return MealSuggesterService(GeminiLLMClient())


@cache
def get_context_builder() -> ContextBuilder:
    return ContextBuilder()


# @cache
# def get_shopping_list_service() -> ShoppingListService:
#     return ShoppingListService()
