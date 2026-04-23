from typing import TYPE_CHECKING, cast

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai_engine.exceptions import AIEngineError

from .services import DietAssistantService

if TYPE_CHECKING:
    from django.contrib.auth.models import User


@login_required
def chat_page(request):
    return render(request, "assistant/chat.html")


class DietAssistantChatAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request) -> Response:
        user_message = str(request.data.get("message", "")).strip()
        user = cast("User", request.user)
        service = DietAssistantService()

        try:
            ai_reply = service.generate_diet_suggestion(
                user=user, user_message=user_message
            )
            return Response({"reply": ai_reply}, status=status.HTTP_200_OK)
        except AIEngineError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:  # noqa: BLE001
            return Response(
                {"detail": f"Erro na IA: {e!s}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
