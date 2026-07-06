from datetime import timedelta

from django.utils import timezone

from apps.academia.models import (
    Exercise,
    FitnessProfile,
    MuscleVolumeGoal,
    WorkoutSession,
)
from apps.academia.schemas import WorkoutPlanSchema
from apps.academia.tools import search_exercises_in_catalog
from core.ai.services import BaseAIGeneratorService
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

    def get_weekly_volume_breakdown(self, user, weeks=1):
        today = timezone.localdate()
        week_ago = today - timedelta(days=7 * weeks)
        breakdown = []
        for key, label in Exercise.MuscleGroupsChoices.choices:
            volume = self._repo.get_volume_by_muscle_group(
                user=user, muscle_group=key, start_date=week_ago, end_date=today
            )
            breakdown.append({"exercise__muscle_group": key, "label": label, "total_volume": volume})
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
        today = timezone.localdate()
        goals = list(
            MuscleVolumeGoal.objects.filter(user=user, period_end__gte=today).order_by(
                "-created_at"
            )
        )
        for goal in goals:
            current_value = self._repo.get_volume_by_muscle_group(
                user=user,
                muscle_group=goal.muscle_group,
                start_date=goal.period_start,
                end_date=goal.period_end,
            )
            is_achieved = goal.target_value > 0 and current_value >= goal.target_value
            if goal.current_value != current_value or goal.is_achieved != is_achieved:
                goal.current_value = current_value
                goal.is_achieved = is_achieved
                goal.save(update_fields=["current_value", "is_achieved"])
        return goals

    def recalculate_goals(self, user):
        today = timezone.localdate()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        previous_week_start = week_start - timedelta(days=7)
        previous_week_end = week_start - timedelta(days=1)

        try:
            profile = FitnessProfile.objects.get(user=user)
            increment = self.INCREMENTS.get(profile.experience_level, 1.10)
        except FitnessProfile.DoesNotExist:
            increment = 1.10

        goals = []
        for key, _label in Exercise.MuscleGroupsChoices.choices:
            baseline_volume = self._repo.get_volume_by_muscle_group(
                user=user,
                muscle_group=key,
                start_date=previous_week_start,
                end_date=previous_week_end,
            )
            current_volume = self._repo.get_volume_by_muscle_group(
                user=user, muscle_group=key, start_date=week_start, end_date=week_end
            )
            existing_goal = MuscleVolumeGoal.objects.filter(
                user=user,
                muscle_group=key,
                period_start=week_start,
                period_end=week_end,
            ).first()

            if baseline_volume > 0:
                target = round(baseline_volume * increment, 2)
            elif existing_goal:
                target = existing_goal.target_value
            elif current_volume > 0:
                target = round(current_volume * increment, 2)
            else:
                continue

            is_achieved = target > 0 and current_volume >= target
            goal_defaults = {
                "target_value": target,
                "current_value": current_volume,
                "metric_unit": "kg*rep",
                "is_achieved": is_achieved,
            }
            if existing_goal:
                for field, value in goal_defaults.items():
                    setattr(existing_goal, field, value)
                existing_goal.save(update_fields=list(goal_defaults.keys()))
                goal = existing_goal
            else:
                goal, _created = MuscleVolumeGoal.objects.update_or_create(
                    user=user,
                    muscle_group=key,
                    period_start=week_start,
                    period_end=week_end,
                    defaults=goal_defaults,
                )
            goals.append(goal)

        return goals


class WorkoutRoutineGeneratorService(BaseAIGeneratorService):
    def build_context(self, user, **kwargs):
        profile = getattr(user, "fitnessprofile", None)
        from apps.academia.dependencies import get_volume_metrics_service
        volume_service = get_volume_metrics_service()
        recent_volume = volume_service.get_weekly_volume_breakdown(user, weeks=1)
        return {
            "profile": {
                "experience_level": profile.experience_level if profile else "beginner",
                "primary_goal": profile.primary_goal if profile else "hypertrophy",
            },
            "recent_volume": recent_volume,
            "request": kwargs,
        }

    def get_system_prompt(self, context):
        profile = context["profile"]
        recent = context["recent_volume"]
        high_volume_muscles = [r["exercise__muscle_group"] for r in recent if (r.get("total_volume") or 0) > 3000]
        return (
            f"Você é um treinador de elite. O usuário é nível {profile['experience_level']}. "
            f"Objetivo: {profile['primary_goal']}. "
            f"Evite sobrecarregar: {', '.join(high_volume_muscles)}. "
            f"Use apenas exercícios do catálogo via search_exercises. "
            f"Gere uma rotina completa em JSON seguindo o schema exato."
        )

    def get_tools(self):
        return [search_exercises_in_catalog]

    def get_response_schema(self):
        return WorkoutPlanSchema

    def format_response(self, raw_json, context):
        return raw_json
