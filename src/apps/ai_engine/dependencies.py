from functools import cache

from .clients.gemini import GeminiLLMClient
from .services import (
    AIEngineService,
    DietAssistantStrategy,
    MealSuggesterService,
    ShoppingListService,
    WeeklyPlannerService,
)


@cache
def get_gemini_client() -> GeminiLLMClient:
    return GeminiLLMClient()


@cache
def get_ai_engine_service() -> AIEngineService:
    strategy = DietAssistantStrategy(get_gemini_client())
    return AIEngineService(strategy=strategy)


@cache
def get_weekly_planner_service() -> WeeklyPlannerService:
    return WeeklyPlannerService(get_gemini_client())


@cache
def get_meal_suggester_service() -> MealSuggesterService:
    return MealSuggesterService(get_gemini_client())


@cache
def get_shopping_list_service() -> ShoppingListService:
    return ShoppingListService(get_gemini_client())
