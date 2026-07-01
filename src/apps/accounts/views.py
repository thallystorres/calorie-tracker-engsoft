from typing import Any, cast

from django.contrib.auth import logout
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .dependencies import get_user_service
from .serializers import (
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
)


class AccountLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        logout(request)  # type: ignore
        return Response(
            {"detail": "Logout realizado com sucesso."}, status=status.HTTP_200_OK
        )


class AccountActivateView(APIView):
    permission_classes = [IsNotAuthenticated]

    def get(self, request: Request) -> Response:
        token = request.query_params.get("token", "").strip()

        if not token:
            return Response(
                {"detail": "Token de ativação ausente."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = get_user_service()
        service.activate_account(token)

        return Response(
            {"detail": "Conta ativada com sucesso."},
            status=status.HTTP_200_OK,
        )


class PasswordResetRequestView(APIView):
    permission_classes = [IsNotAuthenticated]

    def post(self, request: Request) -> Response:
        service = get_user_service()
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast("dict[str, Any]", serializer.validated_data)
        service.request_password_reset(email=validated_data["email"], request=request)
        return Response(
            {
                "detail": (
                    "Se o e-mail informado estiver cadastrado, "
                    "você receberá instruções para redefinir a senha."
                ),
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [IsNotAuthenticated]

    def post(self, request: Request) -> Response:
        token = request.query_params.get("token", "").strip()
        if not token:
            return Response(
                {"detail": "Token de definição ausente."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast("dict[str, Any]", serializer.validated_data)
        service = get_user_service()
        service.reset_password_with_token(
            token=token, new_password=validated_data["new_password"]
        )
        return Response(
            {"detail": "Senha definida com sucesso"}, status=status.HTTP_200_OK
        )
