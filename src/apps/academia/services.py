from datetime import timedelta

from django.utils import timezone

from apps.academia.models import Exercise, FitnessProfile, MuscleVolumeGoal, WorkoutSession
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


class GoalsService:
    INCREMENTS = {
        FitnessProfile.ExperienceLevelChoices.BEGINNER: 1.10,
        FitnessProfile.ExperienceLevelChoices.INTERMEDIARY: 1.07,
        FitnessProfile.ExperienceLevelChoices.ADVANCED: 1.05,
    }

    def __init__(self, workout_repository):
        self._repo = workout_repository

    def get_active_goals(self, user):
        today = timezone.now().date()
        return MuscleVolumeGoal.objects.filter(
            user=user, is_achieved=False, period_end__gte=today
        ).order_by("-created_at")

    def recalculate_goals(self, user):
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        next_week_start = week_end + timedelta(days=1)
        next_week_end = next_week_start + timedelta(days=6)

        try:
            profile = FitnessProfile.objects.get(user=user)
            increment = self.INCREMENTS.get(profile.experience_level, 1.10)
        except FitnessProfile.DoesNotExist:
            increment = 1.10

        goals = []
        for key, _label in Exercise.MuscleGroupsChoices.choices:
            volume = self._repo.get_volume_by_muscle_group(
                user=user, muscle_group=key, start_date=week_start, end_date=week_end
            )
            if volume > 0:
                target = round(volume * increment, 2)
                goal, _created = MuscleVolumeGoal.objects.update_or_create(
                    user=user,
                    muscle_group=key,
                    period_start=next_week_start,
                    period_end=next_week_end,
                    defaults={
                        "target_value": target,
                        "current_value": 0.0,
                        "metric_unit": "kg*rep",
                        "is_achieved": False,
                    },
                )
                goals.append(goal)

        return goals
