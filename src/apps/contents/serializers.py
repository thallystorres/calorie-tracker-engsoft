from rest_framework import serializers
from .models import StudyContent

class StudyContentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyContent
        fields = (
            "name",
            "category",
            "difficulty_level",
        )

    def validate_difficulty_level(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("O nível de dificuldade deve estar entre 1 e 5.")
        return value

class StudyContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyContent
        fields = (
            "id",
            "name",
            "category",
            "difficulty_level",
            "source",
        )
        read_only_fields = ("id", "source")
