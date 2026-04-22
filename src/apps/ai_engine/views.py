from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .clients.gemini import GeminiLLMClient
from .exceptions import AIEngineError
from .services.meal_suggester import MealSuggesterService


class SuggestMealView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        user_prompt = request.data.get("user_prompt", "")

        try:
            # Inicializa o cliente Gemini e o Serviço
            llm_client = GeminiLLMClient()
            service = MealSuggesterService(llm_client=llm_client)

            # Gera a sugestão
            suggestion = service.suggest_meal(
                user=request.user, user_prompt=user_prompt
            )

            # Retorna o dicionário serializado do Pydantic
            return Response(suggestion.model_dump(), status=status.HTTP_200_OK)

        except AIEngineError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"detail": f"Erro interno do motor de IA: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
