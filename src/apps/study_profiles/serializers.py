from rest_framework import serializers
from .models import StudyProfile

class StudyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyProfile
        fields = (
            "weekly_availability_hours",
            "focus_limit_minutes",
            "goal",
            "target_weekly_minutes",
            "target_recall_rate",
            "target_quiz_score",
            "updated_at",
            "remind_interval_hours",
        )
        read_only_fields = ("target_weekly_minutes", "target_recall_rate", "target_quiz_score", "updated_at")
