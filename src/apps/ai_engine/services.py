from pathlib import Path

from django.contrib.auth.models import User

from .clients.base import BaseLLMClient
from .schemas import (
    AIPlannerResponseSchema,
    DietResponseSchema,
    MealSuggestionSchema,
)
from .utils.ai_tools import adjust_future_targets, search_food
from .utils.context_builder import ContextBuilder

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


class WeeklyPlannerService:
    def __init__(self, llm_client: BaseLLMClient):
        self.llm_client = llm_client

    def generate_weekly_plan(self, user: User, user_message: str) -> dict:
        context = ContextBuilder(user).add_profile_data().add_restrictions().build()

        with (PROMPTS_DIR / "weekly_planner.txt").open(encoding="utf-8") as f:
            system_prompt = f.read().format(**context)

        try:
            return self.llm_client.generate_json(
                system_prompt=system_prompt,
                user_prompt=user_message,
                response_schema=AIPlannerResponseSchema,
                tools=[search_food],
            )
        except Exception as e:
            return {
                "state": "asking",
                "message": f"Desculpe, tive um problema ao gerar o plano: {e!s}",
                "weekly_plan": None,
            }


class DietAssistantService:
    def __init__(self, llm_client: BaseLLMClient):
        self.llm_client = llm_client

    def generate_diet_suggestion(self, user: User, user_message: str = "") -> dict:
        context = (
            ContextBuilder(user)
            .add_profile_data()
            .add_daily_progress()
            .add_history()
            .add_restrictions()
            .build()
        )

        with (PROMPTS_DIR / "diet_suggestion.txt").open(encoding="utf-8") as f:
            system_prompt = f.read().format(**context)

        user_message = (
            user_message.strip()
            or "Por favor, monte uma sugestão de dieta para hoje com os alimentos do banco."
        )

        try:
            return self.llm_client.generate_json(
                system_prompt=system_prompt,
                user_prompt=user_message,
                response_schema=DietResponseSchema,
                tools=[search_food],
            )
        except Exception as e:
            return {"texto": "Desculpe, tive um problema de conexão.", "tipo": "chat"}

    def edit_content_with_ai(self, current_content: str, instruction: str) -> str:
        with (PROMPTS_DIR / "edit_diet.txt").open(encoding="utf-8") as f:
            system_prompt = f.read().format(
                current_content=current_content, instruction=instruction
            )

        novo_conteudo = self.llm_client.generate_text(
            system_prompt=system_prompt, user_prompt=instruction, tools=[search_food]
        )
        return novo_conteudo.strip()


class MealSuggesterService:
    def __init__(self, llm_client: BaseLLMClient):
        self.llm_client = llm_client

    def suggest_meal(self, user: User, user_prompt: str) -> MealSuggestionSchema:
        context = (
            ContextBuilder(user)
            .add_profile_data()
            .add_daily_progress()
            .add_history()
            .add_restrictions()
            .build()
        )
        user_id = getattr(user, "id", None)

        with (PROMPTS_DIR / "meal_suggestion.txt").open(encoding="utf-8") as f:
            system_prompt = f.read().format(**context)

        augmented_prompt = (
            f"O ID do usuário atual é {user_id}. Pedido do usuário: {user_prompt}"
        )

        raw_json = self.llm_client.generate_json(
            system_prompt=system_prompt,
            user_prompt=augmented_prompt,
            response_schema=MealSuggestionSchema,
            tools=[search_food, adjust_future_targets],
        )

        suggestion = MealSuggestionSchema.model_validate(raw_json)
        if context.get("historico_insuficiente"):
            suggestion.warning = (
                "Como você tem menos de 7 dias de registros, esta sugestão é genérica."
            )

        return suggestion


class ShoppingListService:
    def __init__(self, llm_client: BaseLLMClient):
        self.llm_client = llm_client

    def generate_shopping_list(self, saved_contents: list[str]) -> str:
        if not saved_contents:
            return (
                "Você ainda não tem dietas ou receitas guardadas para gerar uma lista."
            )

        context = ContextBuilder().add_saved_contents(saved_contents).build()

        with (PROMPTS_DIR / "shopping_list.txt").open(encoding="utf-8") as f:
            system_prompt = f.read().format(**context)

        lista_markdown = self.llm_client.generate_text(
            system_prompt=system_prompt,
            user_prompt="Gere a lista de compras consolidada com base nos meus dados.",
        )
        return lista_markdown.strip()
