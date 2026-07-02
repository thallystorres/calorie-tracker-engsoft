from rest_framework import serializers
from apps.contents.models import StudyContent
from .models import StudySession, StudyItem

class StudyItemInputSerializer(serializers.Serializer):
    content = serializers.PrimaryKeyRelatedField(queryset=StudyContent.objects.all())
    time_minutes = serializers.IntegerField(min_value=1)
    notes = serializers.CharField(allow_blank=True, required=False)

class StudySessionCreateSerializer(serializers.Serializer):
    strategy = serializers.ChoiceField(choices=StudySession.StrategyChoices.choices)
    items = StudyItemInputSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Envie pelo menos um tópico estudado.")
        return value

class StudyItemSerializer(serializers.ModelSerializer):
    content_name = serializers.CharField(source="content.name", read_only=True)

    class Meta:
        model = StudyItem
        fields = ("id", "content", "content_name", "time_minutes", "notes")

class StudySessionSerializer(serializers.ModelSerializer):
    items = StudyItemSerializer(many=True, read_only=True)

    class Meta:
        model = StudySession
        fields = ("id", "strategy", "timestamp", "items")
