from rest_framework import serializers
from .models import NutritionalProfile, FoodRestriction
from django.core.exceptions import ValidationError


class NutritionalProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutritionalProfile
        fields =  (
            "weight_kg",
            "height_cm",
            "age",
            "sex",
            "activity_level",
            "goal",
            "bmr",
            "daily_calorie_target",
            "updated_at",
        )

        read_only_fields = ("bmr", "daily_calorie_target", "updated_at")

class FoodRestrictionSerializer(serializers.ModelSerializer):

    class Meta:
        model = FoodRestriction
        fields = (
            "restriction_type",
            "description"
        )

    def validate(self, attrs):
        restriction_type = attrs.get("restriction_type")
        description = attrs.get("description")

        # Descrição obrigatória se restriction_type for 'OTHER'
        if (
            restriction_type == FoodRestriction.RestrictionTypeChoices.OTHER
            and not description
        ):
            raise ValidationError(
                {
                    "description": "Uma descrição é obrigatória quando 'Outro' for selecionado."
                }
            )

        # Optional: Clear the description if the user selected a standard choice
        if restriction_type != FoodRestriction.RestrictionTypeChoices.OTHER:
            attrs["description"] = ""

        return attrs
