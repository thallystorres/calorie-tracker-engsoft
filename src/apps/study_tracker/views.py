from typing import Any, cast
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .dependencies import get_study_tracker_service
from .serializers import StudySessionCreateSerializer, StudySessionSerializer

class StudySessionCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = StudySessionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast("dict[str, Any]", serializer.validated_data)

        service = get_study_tracker_service()
        session, warnings = service.log_session(
            user=request.user, validated_data=validated_data
        )

        output = StudySessionSerializer(session)

        return Response(
            {
                "detail": "Sessão de estudo registrada com sucesso.",
                "session": output.data,
                "warnings": warnings,
            },
            status=status.HTTP_201_CREATED,
        )
