from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .dependencies import get_profile_service
from .models import FoodRestriction, NutritionalProfile
from .serializers import FoodRestrictionSerializer, NutritionalProfileSerializer


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        """Cria o perfil nutricional (Apenas um por usuário)"""
        # Checa se o usuário já possui um perfil associado
        if hasattr(request.user, "nutritional_profile"):
            return Response(
                {
                    "detail": "Perfil nutricional já existe para este usuário. Use PATCH para atualizar."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = NutritionalProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = NutritionalProfile(user=request.user)

        service = get_profile_service()
        final_profile = service.upsert_profile(profile, serializer.validated_data)

        output_serializer = NutritionalProfileSerializer(final_profile)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request: Request) -> Response:
        """Atualiza campos parciais do perfil (Recalcula TMB e Calorias)"""
        try:
            profile = request.user.nutritional_profile
        except NutritionalProfile.DoesNotExist:
            return Response(
                {"detail": "Perfil Nutricional não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = NutritionalProfileSerializer(
            profile, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)

        service = get_profile_service()

        final_profile = service.upsert_profile(profile, serializer.validated_data)

        output_serializer = NutritionalProfileSerializer(final_profile)
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class FoodRestrictionListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        """Adiciona uma nova restrição alimentar ao perfil do usuário"""
        try:
            profile = request.user.nutritional_profile
        except NutritionalProfile.DoesNotExist:
            return Response(
                {
                    "detail": "Crie um perfil nutricional primeiro antes de adicionar restrições."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = FoodRestrictionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save(profile=profile)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FoodRestrictionDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request: Request, pk: int) -> Response:
        """Remove uma restrição alimentar específica do perfil do usuário"""
        try:
            profile = request.user.nutritional_profile
        except NutritionalProfile.DoesNotExist:
            return Response(
                {"detail": "Perfil Nutricional não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Garante que a restrição existe e pertence ao perfil do usuário autenticado
        restriction = get_object_or_404(FoodRestriction, pk=pk, profile=profile)
        restriction.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
