from rest_framework import serializers

from .models import Exercise, MuscleVolumeGoal, WorkoutSession, WorkoutSet


class WorkoutSetInputSerializer(serializers.Serializer):
    exercise_id = serializers.PrimaryKeyRelatedField(
        queryset=Exercise.objects.all(), source="exercise"
    )
    reps = serializers.IntegerField(min_value=1)
    weight = serializers.FloatField(min_value=0)


class WorkoutCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    duration_minutes = serializers.IntegerField(required=False, allow_null=True)
    sets = WorkoutSetInputSerializer(many=True)

    def validate_sets(self, value):
        if not value:
            raise serializers.ValidationError("Envie pelo menos uma série.")
        return value


class WorkoutSetSerializer(serializers.ModelSerializer):
    exercise_name = serializers.CharField(source="exercise.name", read_only=True)
    muscle_group = serializers.CharField(source="exercise.muscle_group", read_only=True)
    volume = serializers.FloatField(source="get_metric", read_only=True)

    class Meta:
        model = WorkoutSet
        fields = ("id", "exercise", "exercise_name", "muscle_group", "reps", "weight", "volume")


class WorkoutSerializer(serializers.ModelSerializer):
    sets = WorkoutSetSerializer(many=True, read_only=True)
    total_volume = serializers.FloatField(read_only=True)

    class Meta:
        model = WorkoutSession
        fields = ("id", "name", "timestamp", "duration_minutes", "sets", "total_volume")


class MuscleVolumeGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = MuscleVolumeGoal
        fields = (
            "id",
            "muscle_group",
            "target_value",
            "current_value",
            "metric_unit",
            "period_start",
            "period_end",
            "is_achieved",
            "created_at",
        )


class GenerateRoutineRequestSerializer(serializers.Serializer):
    split_type = serializers.CharField(max_length=50, required=False, default="full_body")
    days_per_week = serializers.IntegerField(min_value=1, max_value=7, required=False, default=3)


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ("id", "name", "muscle_group", "description")
