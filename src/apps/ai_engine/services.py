from pathlib import Path
from django.contrib.auth.models import User

from core.ai_engine.generator import BaseAIGeneratorService
from core.exceptions import LLMRequestError, LLMResponseError


from .schemas import (
    AIPlannerResponseSchema,
    DietResponseSchema,
    MealSuggestionSchema,
)
from .utils.ai_tools import adjust_future_targets, search_food
from .utils.context_builder import ContextBuilder

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


class WeeklyPlannerService(BaseAIGeneratorService):
    def build_context(self, user: User | None, **kwargs) -> dict:
        return ContextBuilder(user).add_profile_data().add_restrictions().build()

    def get_system_prompt(self, context: dict) -> str:
        with (PROMPTS_DIR / "weekly_planner.txt").open(encoding="utf-8") as f:
            return f.read().format(**context)

    def get_response_schema(self):
        return AIPlannerResponseSchema

    def get_tools(self):
        return [search_food]

    def generate_weekly_plan(self, user: User, user_message: str) -> dict:
        try:
            return self.generate(user=user, user_prompt=user_message)
        except (LLMRequestError, LLMResponseError) as e:
            return {
                "state": "asking",
                "message": f"Desculpe, tive um problema ao gerar o plano: {e!s}",
                "weekly_plan": None,
            }


class DietAssistantService(BaseAIGeneratorService):
    def build_context(self, user: User | None, **kwargs) -> dict:
        return (
            ContextBuilder(user)
            .add_profile_data()
            .add_daily_progress()
            .add_history()
            .add_restrictions()
            .build()
        )

    def get_system_prompt(self, context: dict) -> str:
        with (PROMPTS_DIR / "diet_suggestion.txt").open(encoding="utf-8") as f:
            return f.read().format(**context)

    def get_response_schema(self):
        return DietResponseSchema

    def get_tools(self):
        return [search_food]

    def augment_user_prompt(self, user: User | None, prompt: str) -> str:
        return prompt.strip() or "Por favor, monte uma sugestão de dieta para hoje com os alimentos do banco."

    def generate_diet_suggestion(self, user: User, user_message: str = "") -> dict:
        try:
            return self.generate(user=user, user_prompt=user_message)
        except (LLMRequestError, LLMResponseError) as e:
            return {"texto": f"Desculpe, tive um problema de conexão: {e!s}", "tipo": "chat"}

    def edit_content_with_ai(self, current_content: str, instruction: str) -> str:
        with (PROMPTS_DIR / "edit_diet.txt").open(encoding="utf-8") as f:
            system_prompt = f.read().format(
                current_content=current_content, instruction=instruction
            )
        return self.llm_client.generate_text(
            system_prompt=system_prompt, user_prompt=instruction, tools=[search_food]
        ).strip()


class MealSuggesterService(BaseAIGeneratorService):
    def build_context(self, user: User | None, **kwargs) -> dict:
        return (
            ContextBuilder(user)
            .add_profile_data()
            .add_daily_progress()
            .add_history()
            .add_restrictions()
            .build()
        )

    def get_system_prompt(self, context: dict) -> str:
        with (PROMPTS_DIR / "meal_suggestion.txt").open(encoding="utf-8") as f:
            return f.read().format(**context)

    def get_response_schema(self):
        return MealSuggestionSchema

    def get_tools(self):
        return [search_food, adjust_future_targets]

    def augment_user_prompt(self, user: User | None, prompt: str) -> str:
        user_id = getattr(user, "id", None)
        return f"O ID do usuário atual é {user_id}. Pedido do usuário: {prompt}"

    def format_response(self, raw_json: dict, context: dict) -> MealSuggestionSchema:
        suggestion = MealSuggestionSchema.model_validate(raw_json)
        if context.get("historico_insuficiente"):
            suggestion.warning = "Como você tem menos de 7 dias de registros, esta sugestão é genérica."
        return suggestion

    def suggest_meal(self, user: User, user_prompt: str) -> MealSuggestionSchema:
        return self.generate(user=user, user_prompt=user_prompt)


class ShoppingListService(BaseAIGeneratorService):
    def build_context(self, user: User | None, **kwargs) -> dict:
        saved_contents = kwargs.get("saved_contents", [])
        return ContextBuilder().add_saved_contents(saved_contents).build()

    def get_system_prompt(self, context: dict) -> str:
        with (PROMPTS_DIR / "shopping_list.txt").open(encoding="utf-8") as f:
            return f.read().format(**context)

    def generate_shopping_list(self, saved_contents: list[str]) -> str:
        if not saved_contents:
            return "Você ainda não tem dietas ou receitas guardadas para gerar uma lista."

        return self.generate(
            user=None,
            user_prompt="Gere a lista de compras consolidada com base nos meus dados.",
            saved_contents=saved_contents
        ).strip()
