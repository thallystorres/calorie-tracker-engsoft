from django.contrib.auth.models import User
from django.db.models import Sum, QuerySet
from django.db.models.functions import TruncDate
from core.tracking.repositories import BaseTrackerRepository
from .models import StudySession, StudyItem

class StudySessionRepository(BaseTrackerRepository[StudySession, StudyItem]):
    def __init__(self):
        super().__init__(event_model=StudySession, item_model=StudyItem)

    def create_items(self, event: StudySession, items_data: list[dict]) -> list[StudyItem]:
        items = [
            self.item_model(
                session=event,
                content_id=data["content"].id, # Ajustado para parear com o serializer
                time_minutes=data["time_minutes"],
                notes=data.get("notes", "")
            )
            for data in items_data
        ]
        return self.item_model.objects.bulk_create(items)

    def get_daily_totals(self, user: User, date) -> dict:
        qs = StudyItem.objects.filter(session__user=user, session__timestamp__date=date)
        return qs.aggregate(total_minutes=Sum("time_minutes"))

    def get_period_daily_totals(self, user: User, start_date, end_date) -> QuerySet:
        qs = StudyItem.objects.filter(
            session__user=user,
            session__timestamp__date__gte=start_date,
            session__timestamp__date__lte=end_date,
        )
        return (
            qs.annotate(day=TruncDate("session__timestamp"))
            .values("day")
            .annotate(total_minutes=Sum("time_minutes"))
            .order_by("-day")
        )
