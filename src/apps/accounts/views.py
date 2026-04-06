from typing import Any, cast

from django.contrib.auth import login, logout
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


class IsNotAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):  # type: ignore
        return not request.user.is_authenticated


class AccountRegisterView(APIView):
    permission_classes = [IsNotAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = AccountRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast("dict[str, Any]", serializer.validated_data)

        user = UserService.create_account(validated_data=validated_data)
        output = AccountSerializer(user)
        return Response(output.data, status=status.HTTP_201_CREATED)


class AccountMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        serializer = AccountSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request: Request) -> Response:
        request_user = request.user
        serializer = AccountSerializer(request_user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        validated_data = cast("dict[str, Any]", serializer.validated_data)
        user = UserService.update_account_profile(
            user=request_user, validated_data=validated_data
        )
        output = AccountSerializer(user)
        return Response(output.data, status=status.HTTP_200_OK)


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
