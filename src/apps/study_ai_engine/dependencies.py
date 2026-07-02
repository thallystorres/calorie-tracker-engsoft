from functools import cache
from core.ai_engine.clients.gemini import GeminiLLMClient
from .services import QuizGeneratorService, FlashcardGeneratorService

@cache
def get_llm_client():
    return GeminiLLMClient()

@cache
def get_quiz_generator_service() -> QuizGeneratorService:
    return QuizGeneratorService(llm_client=get_llm_client())

@cache
def get_flashcard_generator_service() -> FlashcardGeneratorService:
    return FlashcardGeneratorService(llm_client=get_llm_client())
