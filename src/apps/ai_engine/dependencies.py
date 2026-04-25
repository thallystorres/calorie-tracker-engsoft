from functools import cache

from .clients.gemini import GeminiLLMClient
from .services import DietAssistantService, MealSuggesterService, ShoppingListService


@cache
def get_gemini_client() -> GeminiLLMClient:
    return GeminiLLMClient()


@cache
def get_diet_assistant_service() -> DietAssistantService:
    return DietAssistantService(get_gemini_client())


@cache
def get_meal_suggester_service() -> MealSuggesterService:
    return MealSuggesterService(get_gemini_client())


@cache
def get_shopping_list_service() -> ShoppingListService:
    return ShoppingListService(get_gemini_client())
