from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import FoodRestriction, NutritionalProfile


class NutritionalProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionalProfile
        fields = (
            "weight_kg",
            "height_cm",
            "age",
            "sex",
            "activity_level",
            "goal",
            "bmr",
            "daily_calorie_target",
            "updated_at",
            "remind_interval_hours",
        )

        read_only_fields = ("bmr", "daily_calorie_target", "updated_at")


class FoodRestrictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodRestriction
        fields = ("id", "restriction_type", "description")

    def validate(self, attrs):
        restriction_type = attrs.get("restriction_type")
        description = attrs.get("description")

        if (
            restriction_type == FoodRestriction.RestrictionTypeChoices.OTHER
            and not description
        ):
            raise ValidationError(
                {
                    "description": "Uma descrição é obrigatória quando 'Outro' for selecionado."
                }
            )

        if restriction_type != FoodRestriction.RestrictionTypeChoices.OTHER:
            attrs["description"] = ""

        return attrs
