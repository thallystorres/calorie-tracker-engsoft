from typing import Any, cast

from django.contrib.auth import login, logout
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .dependencies import get_user_service
from .serializers import (
    AccountDeleteSerializer,
    AccountLoginSerializer,
    AccountRegisterSerializer,
    AccountSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
)


class IsNotAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):  # type: ignore
        return not request.user.is_authenticated


class AccountRegisterView(APIView):
    permission_classes = [IsNotAuthenticated]

    def post(self, request: Request) -> Response:
        service = get_user_service()
        serializer = AccountRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast("dict[str, Any]", serializer.validated_data)

        user = service.create_account(validated_data=validated_data, request=request)

        output = AccountSerializer(user)
        return Response(
            {
                "detail": "Conta criada com sucesso. Verifique seu e-mail para ativar.",
                "user": output.data,
            },
            status=status.HTTP_201_CREATED,
        )


class AccountMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        serializer = AccountSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request: Request) -> Response:
        service = get_user_service()
        request_user = request.user
        serializer = AccountSerializer(request_user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        validated_data = cast("dict[str, Any]", serializer.validated_data)
        user, email_changed = service.update_account(
            user=request_user, validated_data=validated_data, request=request
        )

        detail = "Conta atualizada com sucesso. "
        if email_changed:
            logout(request)  # type: ignore
            detail = (
                detail + "Sua sessão foi encerrada. "
                "Verifique seu e-mail para reativar a conta."
            )

        output = AccountSerializer(user)
        return Response(
            {
                "detail": detail,
                "user": output.data,
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request: Request) -> Response:
        service = get_user_service()
        serializer = AccountDeleteSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        service.delete_account(user=request.user)
        logout(request)  # type:ignore
        return Response(status=status.HTTP_204_NO_CONTENT)


class AccountLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request: Request) -> Response:
        serializer = AccountLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast("dict[str, Any]", serializer.validated_data)
        user = validated_data["user"]

        login(request, user)  # type: ignore

        return Response(
            {"detail": "Login realizado com sucesso."}, status=status.HTTP_200_OK
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

        try:
            service = get_user_service()
            service.activate_account(token)
        except ValidationError as e:
            return Response({"detail": e.detail}, status=status.HTTP_400_BAD_REQUEST)

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
        try:
            service = get_user_service()
            service.reset_password_with_token(
                token=token, new_password=validated_data["new_password"]
            )
        except ValidationError as e:
            return Response({"detail": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {"detail": "Senha definida com sucesso"}, status=status.HTTP_200_OK
        )
