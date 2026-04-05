from typing import Any, cast

from django.contrib.auth import login
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from src.apps.accounts.services import UserService

from .serializers import (
    AccountLoginSerializer,
    AccountRegisterSerializer,
    AccountSerializer,
)


class AccountRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request: Request) -> Response:
        serializer = AccountRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast("dict[str, Any]", serializer.validated_data)

        user = UserService.create_account(validated_data=validated_data)
        output = AccountSerializer(user)
        return Response(output.data, status=status.HTTP_201_CREATED)


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
            {"detail:Logout realizado com sucesso."}, status=status.HTTP_200_OK
        )
