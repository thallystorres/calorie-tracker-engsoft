from typing import Any, cast

from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import MealCreateSerializer, MealSerializer
from .services import TrackerService


class MealCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = MealCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast("dict[str, Any]", serializer.validated_data)

        service = TrackerService()
        meal, warnings = service.log_meal(
            user=request.user, validated_data=validated_data
        )

        output = MealSerializer(meal)

        return Response(
            {
                "detail": "Refeição registrada com sucesso.",
                "meal": output.data,
                "warnings": warnings,
            },
            status=status.HTTP_201_CREATED,
        )
