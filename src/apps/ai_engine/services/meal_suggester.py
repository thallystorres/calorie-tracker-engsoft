from pathlib import Path

from django.contrib.auth.models import User
from pydantic import BaseModel

from apps.ai_engine.services.ai_tools import adjust_future_targets, search_food
from apps.ai_engine.services.context_builder import ContextBuilderService

from ..clients.base import BaseLLMClient


class IngredientSchema(BaseModel):
    name: str
    quantity_grams: float


class TargetAdjustmentSchema(BaseModel):
    applied: bool
    description: str


class MealSuggestionSchema(BaseModel):
    meal_name: str
    ingredients: list[IngredientSchema]
    estimated_calories: float
    target_adjustments: TargetAdjustmentSchema
    warning: str | None = None  # <-- Novo campo opcional


class MealSuggesterService:
    _PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "system.txt"

    def __init__(self, llm_client: BaseLLMClient):
        self.llm_client = llm_client
        self.context_builder = ContextBuilderService()

    def suggest_meal(self, user: User, user_prompt: str) -> MealSuggestionSchema:
        context = self.context_builder.get_user_context(user)
        user_id = getattr(user, "id", None)

        with self._PROMPT_PATH.open(encoding="utf-8") as f:
            system_prompt_template = f.read()

        system_prompt = system_prompt_template.format(**context)

        tools = [search_food, adjust_future_targets]
        augmented_prompt = (
            f"O ID do usuário atual é {user_id}. Pedido do usuário: {user_prompt}"
        )

        raw_json = self.llm_client.generate_json(
            system_prompt=system_prompt,
            user_prompt=augmented_prompt,
            response_schema=MealSuggestionSchema,
            tools=tools,
        )

        suggestion = MealSuggestionSchema.model_validate(raw_json)

        # Injeta o aviso no backend, poupando tokens da LLM
        if context.get("historico_insuficiente"):
            suggestion.warning = "Como você tem menos de 7 dias de registros, esta sugestão é genérica e baseada em dados limitados. Com o tempo, a calorIA aprenderá suas preferências reais!"

        return suggestion
