from typing import cast
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User

from .dependencies import get_quiz_generator_service, get_flashcard_generator_service

class GenerateQuizAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request) -> Response:
        user_message = str(request.data.get("topic", "")).strip()
        user = cast(User, request.user)

        service = get_quiz_generator_service()
        try:
            ai_reply_data = service.generate(user=user, user_prompt=user_message)
            return Response(ai_reply_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GenerateFlashcardsAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request: Request) -> Response:
        user_message = str(request.data.get("topic", "")).strip()
        user = cast(User, request.user)

        service = get_flashcard_generator_service()
        try:
            ai_reply_data = service.generate(user=user, user_prompt=user_message)
            return Response(ai_reply_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
