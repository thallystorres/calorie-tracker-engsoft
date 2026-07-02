from datetime import timedelta

from django.utils import timezone

from apps.academia.models import Exercise, WorkoutSession
from core.tracking.services import BaseTrackerService


class WorkoutTrackerService(BaseTrackerService):
    def __init__(self, workout_repository):
        super().__init__(repository=workout_repository)

    def validate_event_against_profile(self, user, items_data):
        warnings = []
        muscle_groups = set(item["exercise"].muscle_group for item in items_data)

        recent_sessions = WorkoutSession.objects.filter(
            user=user, timestamp__gte=timezone.now() - timedelta(hours=24)
        ).prefetch_related("sets__exercise")
        trained_groups = set(
            s.exercise.muscle_group
            for session in recent_sessions
            for s in session.sets.all()
        )

        overlap = muscle_groups & trained_groups
        if overlap:
            groups_pt = [
                dict(Exercise.MuscleGroupsChoices.choices).get(g, g)
                for g in overlap
            ]
            warnings.append(
                f"Atenção: Overtraining detectado. "
                f"Grupos musculares {', '.join(groups_pt)} já treinados nas últimas 24h."
            )
        return warnings


class VolumeMetricsService:
    def __init__(self, workout_repository):
        self._repo = workout_repository

    def get_volume_by_muscle_group(self, user, muscle_group):
        return self._repo.get_volume_by_muscle_group(user=user, muscle_group=muscle_group)

    def get_weekly_volume_breakdown(self, user):
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        breakdown = {}
        for key, label in Exercise.MuscleGroupsChoices.choices:
            volume = self._repo.get_volume_by_muscle_group(
                user=user, muscle_group=key, start_date=week_ago, end_date=today
            )
            breakdown[key] = {"label": label, "total_volume": volume}
        return breakdown
