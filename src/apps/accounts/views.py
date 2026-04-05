from typing import Any, cast

from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from src.apps.accounts.services import UserService

from .serializers import (
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
