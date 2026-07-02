from django.contrib.auth.models import User
from django.db.models import Sum, F
from pgvector.django import L2Distance

from core.tracking.repositories import BaseTrackerRepository

from .models import Exercise, WorkoutSession, WorkoutSet


class WorkoutRepository(BaseTrackerRepository[WorkoutSession, WorkoutSet]):
    def __init__(self):
        super().__init__(event_model=WorkoutSession, item_model=WorkoutSet)

    def create_items(self, event, items_data):
        items = [
            self.item_model(
                session=event,
                exercise=data["exercise"],
                reps=data["reps"],
                weight=data["weight"],
            )
            for data in items_data
        ]
        return self.item_model.objects.bulk_create(items)

    def list_sessions_for_user(self, user: User):
        return (
            WorkoutSession.objects.filter(user=user)
            .prefetch_related("sets__exercise")
            .order_by("-timestamp")
        )

    def get_volume_by_muscle_group(self, user: User, muscle_group: str, start_date=None, end_date=None):
        qs = WorkoutSet.objects.filter(
            session__user=user,
            exercise__muscle_group=muscle_group,
        )
        if start_date:
            qs = qs.filter(session__timestamp__date__gte=start_date)
        if end_date:
            qs = qs.filter(session__timestamp__date__lte=end_date)

        result = qs.aggregate(total=Sum(F("reps") * F("weight")))
        return result["total"] or 0.0

    def search_exercises_semantic(self, embedding: list[float], limit: int = 5):
        """
        Busca exercícios semanticamente similares usando distância L2.
        """
        return (
            Exercise.objects.annotate(distance=L2Distance("embedding", embedding))
            .order_by("distance")[:limit]
        )
