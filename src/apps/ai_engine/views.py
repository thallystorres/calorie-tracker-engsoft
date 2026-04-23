from typing import cast

from django.contrib.auth.models import User
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .dependencies import get_meal_suggester_service
from .exceptions import AIEngineError


class SuggestMealView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        user_prompt = request.data.get("user_prompt", "")
        user = cast("User", request.user)

        try:
            service = get_meal_suggester_service()

            suggestion = service.suggest_meal(
                user=user, user_prompt=str(user_prompt).strip()
            )

            return Response(suggestion.model_dump(), status=status.HTTP_200_OK)

        except AIEngineError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"detail": f"Erro interno do motor de IA: {e!s}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
