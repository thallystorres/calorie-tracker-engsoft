from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import DietAssistantService


@login_required
def chat_page(request):
  return render(request, "assistant/chat.html")


class DietAssistantChatAPIView(APIView):
  permission_classes = [permissions.IsAuthenticated]

  def post(self, request: Request) -> Response:
    user_message = request.data.get("message", "")
    service = DietAssistantService()

    try:
      ai_reply = service.generate_diet_suggestion(
        user=request.user,
        user_message=user_message
      )
      return Response({"reply": ai_reply}, status=status.HTTP_200_OK)
    except Exception as e:
      return Response(
        {"detail": f"Erro na IA: {str(e)}"},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
      )
