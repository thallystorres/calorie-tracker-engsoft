from datetime import timedelta

from django.utils import timezone

from apps.academia.models import Exercise, WorkoutSession
from core.tracking.services import BaseTrackerService


class WorkoutTrackerService(BaseTrackerService):
    def __init__(self, work_out_repository):
        super().__init__(repository=work_out_repository)

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

        overlap = muscle_groups.intersection(trained_groups)
        if overlap:
            groups_pt = [Exercise.MuscleGroupsChoices(g).label for g in overlap]
            warnings.append(
                f"Atenção: Overtraining detectado. "
                f"Grupos musculares {', '.join(groups_pt)} já treinados nas últimas 24h."
            )
        return warnings
