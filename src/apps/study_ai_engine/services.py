from django.contrib.auth.models import User
from core.ai_engine.generator import BaseAIGeneratorService
from .schemas import FlashcardSetResponseSchema, QuizResponseSchema
from .utils.context_builder import StudyContextBuilder
from .utils.ai_tools import search_study_content

class QuizGeneratorService(BaseAIGeneratorService):
    def build_context(self, user: User | None, **kwargs) -> dict:
        return StudyContextBuilder(user).add_profile_data().add_history_and_notes().build()

    def get_system_prompt(self, context: dict) -> str:
        return (
            f"Gere um Simulado com base no tópico pedido pelo usuário. "
            f"O objetivo do aluno é {context.get('objetivo', 'Estudos Gerais')}. "
            f"Incorpore as anotações prévias do aluno para testar o entendimento real:\n"
            f"{context.get('anotacoes')}"
        )

    def get_response_schema(self):
        return QuizResponseSchema

    def get_tools(self):
        return [search_study_content]

class FlashcardGeneratorService(BaseAIGeneratorService):
    def build_context(self, user: User | None, **kwargs) -> dict:
        return StudyContextBuilder(user).add_profile_data().add_history_and_notes().build()

    def get_system_prompt(self, context: dict) -> str:
        return (
            f"Crie um baralho de Flashcards diretos baseados no tópico pedido e nas anotações do aluno:\n"
            f"{context.get('anotacoes')}"
        )

    def get_response_schema(self):
        return FlashcardSetResponseSchema

    def get_tools(self):
        return [search_study_content]
