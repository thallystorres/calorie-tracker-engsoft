import json

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .dependencies import get_food_restriction_repository, get_profile_service
from .models import FoodRestriction, NutritionalProfile
from .serializers import FoodRestrictionSerializer, NutritionalProfileSerializer


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @staticmethod
    def _parse_restrictions_payload(raw_value: object) -> list[dict] | None:
        if raw_value is None or raw_value == "":
            return None

        if isinstance(raw_value, str):
            try:
                parsed = json.loads(raw_value)
            except json.JSONDecodeError as exc:
                raise ValidationError({"restrictions": "JSON inválido."}) from exc
            if isinstance(parsed, list):
                return parsed
            raise ValidationError({"restrictions": "Formato inválido."})

        if isinstance(raw_value, list):
            return raw_value

        raise ValidationError({"restrictions": "Formato inválido."})

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

        restrictions_payload = self._parse_restrictions_payload(
            request.data.get("restrictions")
        )
        if restrictions_payload is not None:
            restrictions_serializer = FoodRestrictionSerializer(
                data=restrictions_payload, many=True
            )
            restrictions_serializer.is_valid(raise_exception=True)
            service.replace_restrictions(
                profile=final_profile,
                restrictions_data=restrictions_serializer.validated_data,
            )

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

        restrictions_payload = self._parse_restrictions_payload(
            request.data.get("restrictions")
        )
        if restrictions_payload is not None:
            restrictions_serializer = FoodRestrictionSerializer(
                data=restrictions_payload, many=True
            )
            restrictions_serializer.is_valid(raise_exception=True)
            service.replace_restrictions(
                profile=final_profile,
                restrictions_data=restrictions_serializer.validated_data,
            )

        output_serializer = NutritionalProfileSerializer(final_profile)
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class FoodRestrictionListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
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

    def get(self, request: Request) -> Response:
        try:
            profile = request.user.nutritional_profile

        except NutritionalProfile.DoesNotExist:
            return Response(
                {"detail": "Perfil Nutricional não encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        restrictions = get_food_restriction_repository().search_profile(profile)
        serializer = FoodRestrictionSerializer(restrictions, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


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
