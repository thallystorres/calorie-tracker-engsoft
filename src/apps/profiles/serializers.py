from rest_framework import serializers
from .models import NutritionalProfile


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

        read_only_fiealds = ("bmr", "daily_calorie_target", "updated_at")
