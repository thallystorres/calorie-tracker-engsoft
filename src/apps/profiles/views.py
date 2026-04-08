from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .dependencies import get_profile_service
from .models import NutritionalProfile
from .serializers import NutritionalProfileSerializer

class ProfileMeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        try:
            profile = request.user.nutritional_profile
            serializer = NutritionalProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except NutritionalProfile.DoesNotExist:
            return Response(
                {"detail": "Perfil Nutricional não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def put(self, request: Request) -> Response:
        try:
            profile = request.user.nutritional_profile
        except NutritionalProfile.DoesNotExist:
            profile = NutritionalProfile(user=request.user)

        serializer = NutritionalProfileSerializer(profile, data=request.data)
        serializer.is_valid(raise_exception=True)

        service = get_profile_service()
        final_profile = service.upsert_profile(profile, serializer.validated_data)

        output_serializer = NutritionalProfileSerializer(final_profile)

        return Response(output_serializer.data, status=status.HTTP_200_OK)
