from decimal import Decimal

from rest_framework import serializers

from apps.foods.models import Food

from .models import Meal, MealItem


class MealItemInputSerializer(serializers.Serializer):
    food_id = serializers.PrimaryKeyRelatedField(queryset=Food.objects.all())
    quantity_grams = serializers.DecimalField(
        max_digits=7, decimal_places=2, min_value=Decimal("0.1")
    )


class MealCreateSerializer(serializers.Serializer):
    label = serializers.ChoiceField(choices=Meal.MealLabel.choices)
    items = MealItemInputSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Envie pelo menos um item.")
        return value


class MealItemSerializer(serializers.ModelSerializer):
    food_name = serializers.CharField(source="food.name", read_only=True)

    class Meta:
        model = MealItem
        fields = ("id", "food", "food_name", "quantity_grams", "kcal_total")


class MealSerializer(serializers.ModelSerializer):
    items = MealItemSerializer(many=True, read_only=True)

    class Meta:
        model = Meal
        fields = ("id", "label", "eaten_at", "items")
