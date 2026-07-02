from typing import Any, cast

from rest_framework import permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .dependencies import (
    get_tracker_service,
    get_workout_repository,
)
from .serializers import (
    WorkoutCreateSerializer,
    WorkoutSerializer,
)


class WorkoutListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        repo = get_workout_repository()
        sessions = repo.list_sessions_for_user(user=request.user)

        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(sessions, request, view=self)
        serializer = WorkoutSerializer(page, many=True)
        return paginator.get_paginated_response(data=serializer.data)

    def post(self, request: Request) -> Response:
        serializer = WorkoutCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast("dict[str, Any]", serializer.validated_data)

        event_data = {
            "name": validated_data["name"],
            "duration_minutes": validated_data.get("duration_minutes"),
        }
        items_data = validated_data["sets"]

        service = get_tracker_service()
        event, warnings = service.log_event(
            user=request.user, event_data=event_data, items_data=items_data
        )

        output = WorkoutSerializer(event)
        return Response(
            {
                "detail": "Treino registrado com sucesso.",
                "workout": output.data,
                "warnings": warnings,
            },
            status=status.HTTP_201_CREATED,
        )
