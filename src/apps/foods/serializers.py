from rest_framework import serializers

from .models import Food


class FoodCreateSerializer(serializers.ModelSerializer):
    kcal_per_100g = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False
    )

    class Meta:
        model = Food
        fields = (
            "name",
            "kcal_per_100g",
            "protein_per_100g",
            "carbs_per_100g",
            "fat_per_100g",
            "fiber_per_100g",
        )

    def validate(self, attrs):
        attrs["source"] = Food.FoodSource.MANUAL

        if attrs.get("kcal_per_100g") is None:
            protein = attrs.get("protein_per_100g")
            carbs = attrs.get("carbs_per_100g")
            fat = attrs.get("fat_per_100g")

            if protein is None or carbs is None or fat is None:
                raise serializers.ValidationError(
                    "Para calcular kcal automaticamente, protein_per_100g,"
                    " carbs_per_100g e fat_per_100g são obrigatórios."
                )
            attrs["kcal_per_100g"] = Food.calculate_kcal_per_100g(
                protein_per_100g=protein,
                carbs_per_100g=carbs,
                fat_per_100g=fat,
            )
        return attrs


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = (
            "id",
            "name",
            "kcal_per_100g",
            "protein_per_100g",
            "carbs_per_100g",
            "fat_per_100g",
            "fiber_per_100g",
            "source",
        )
        read_only = ("id", "source")
