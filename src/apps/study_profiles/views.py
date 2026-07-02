from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .dependencies import get_study_profile_service
from .models import StudyProfile
from .serializers import StudyProfileSerializer
from .services import get_profile_or_404

class StudyProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        if hasattr(request.user, "study_profile"):
            return Response(
                {"detail": "Perfil de estudos já existe para este usuário. Use PATCH para atualizar."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = StudyProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = StudyProfile(user=request.user)
        service = get_study_profile_service()
        final_profile = service.upsert_profile(profile, serializer.validated_data)

        output_serializer = StudyProfileSerializer(final_profile)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request: Request) -> Response:
        profile = get_profile_or_404(request.user)
        serializer = StudyProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        service = get_study_profile_service()
        final_profile = service.upsert_profile(profile, serializer.validated_data)

        output_serializer = StudyProfileSerializer(final_profile)
        return Response(output_serializer.data, status=status.HTTP_200_OK)
