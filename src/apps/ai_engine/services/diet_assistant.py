from pathlib import Path

from django.contrib.auth.models import User
from pydantic import BaseModel, Field

from apps.ai_engine.services.ai_tools import search_food
from src.apps.ai_engine.clients.base import BaseLLMClient

from .context_builder import ContextBuilder


class DietResponseSchema(BaseModel):
    tipo: str = Field(
        description="Classifique a resposta estritamente como 'dieta', 'receita' ou 'chat'"
    )
    texto: str = Field(
        description="A sua resposta redigida para o utilizador, formatada em Markdown limpo"
    )


class DietAssistantService:
    _PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

    def __init__(self, llm_client: BaseLLMClient):
        self.llm_client = llm_client

    def generate_diet_suggestion(self, user: User, user_message: str = "") -> dict:
        context = (
            ContextBuilder(user)
            .add_profile_data()
            .add_history()
            .add_restrictions()
            .build()
        )

        with (self._PROMPTS_DIR / "diet_suggestion.txt").open(encoding="utf-8") as f:
            system_prompt = f.read().format(**context)

        if not user_message or not user_message.strip():
            user_message = "Por favor, monte uma sugestão de dieta para hoje com os alimentos do banco."

        try:
            return self.llm_client.generate_json(
                system_prompt=system_prompt,
                user_prompt=user_message,
                response_schema=DietResponseSchema,
                tools=[search_food],
            )
        except Exception as e:
            print(f"Erro detalhado na execução da IA: {e}")
            return {
                "texto": "Desculpe, tive um problema ao tentar acessar o banco de dados de alimentos.",
                "tipo": "chat",
            }

    def edit_content_with_ai(self, current_content: str, instruction: str) -> str:
        with (self._PROMPTS_DIR / "edit_diet.txt").open(encoding="utf-8") as f:
            system_prompt = f.read().format(
                current_content=current_content, instruction=instruction
            )

        try:
            novo_conteudo = self.llm_client.generate_text(
                system_prompt=system_prompt,
                user_prompt=instruction,
                tools=[search_food],
            )
            return novo_conteudo.strip()
        except Exception as e:
            print(f"Erro na edição por IA: {e}")
            raise Exception("Falha ao editar com a IA.")

    def generate_shopping_list(self, saved_contents: list[str]) -> str:
        if not saved_contents:
            return (
                "Você ainda não tem dietas ou receitas guardadas para gerar uma lista."
            )

        context = ContextBuilder().add_saved_contents(saved_contents).build()

        with (self._PROMPTS_DIR / "shopping_list.txt").open(encoding="utf-8") as f:
            system_prompt = f.read().format(**context)

        try:
            lista_markdown = self.llm_client.generate_text(
                system_prompt=system_prompt,
                user_prompt="Gere a lista de compras consolidada com base nos meus dados.",
            )
            return lista_markdown.strip()
        except Exception as e:
            print(f"Erro ao gerar lista de compras: {e}")
            return "Desculpe, ocorreu um erro ao processar a sua lista de compras."
