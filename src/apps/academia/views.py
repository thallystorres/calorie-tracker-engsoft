from typing import Any, cast

from rest_framework import permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .dependencies import (
    get_goals_service,
    get_routine_generator_service,
    get_tracker_service,
    get_volume_metrics_service,
    get_workout_repository,
)
from .models import Exercise
from .serializers import (
    ExerciseSerializer,
    GenerateRoutineRequestSerializer,
    MuscleVolumeGoalSerializer,
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


class VolumeMetricsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        muscle_group = request.query_params.get("muscle_group")
        if not muscle_group:
            return Response(
                {"detail": "Parametro muscle_group e obrigatorio."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = get_volume_metrics_service()
        volume = service.get_volume_by_muscle_group(
            user=request.user, muscle_group=muscle_group
        )
        return Response(
            {"muscle_group": muscle_group, "total_volume": volume},
            status=status.HTTP_200_OK,
        )


class WeeklyVolumeMetricsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        service = get_volume_metrics_service()
        breakdown = service.get_weekly_volume_breakdown(user=request.user)
        return Response(breakdown, status=status.HTTP_200_OK)


class GoalsListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        service = get_goals_service()
        goals = service.get_active_goals(user=request.user)
        serializer = MuscleVolumeGoalSerializer(goals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GoalsRecalculateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        service = get_goals_service()
        goals = service.recalculate_goals(user=request.user)
        serializer = MuscleVolumeGoalSerializer(goals, many=True)
        return Response(
            {
                "detail": "Metas recalculadas com sucesso.",
                "goals": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class GenerateRoutineView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = GenerateRoutineRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = get_routine_generator_service()
        plan = service.generate(
            user=request.user,
            user_prompt=f"Crie uma rotina {serializer.validated_data.get('split_type')} para {serializer.validated_data.get('days_per_week')} dias",
            split_type=serializer.validated_data.get("split_type"),
            days_per_week=serializer.validated_data.get("days_per_week"),
        )
        return Response(plan, status=status.HTTP_200_OK)


class ExerciseListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        repo = get_workout_repository()
        query = request.query_params.get("q")
        if query:
            from core.ai.services import GeminiLLMClient
            client = GeminiLLMClient()
            try:
                embedding = client.get_embedding(query, task_type="search_query")
                exercises = repo.search_exercises_semantic(embedding, limit=20)
            except Exception:
                exercises = Exercise.objects.filter(name__icontains=query)[:20]
        else:
            exercises = Exercise.objects.all().order_by("name")
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(exercises, request, view=self)
        serializer = ExerciseSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
