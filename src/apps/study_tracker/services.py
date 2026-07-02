from django.contrib.auth.models import User
from core.tracking.services import BaseTrackerService
from .repositories import StudySessionRepository

class StudyTrackerService(BaseTrackerService):
    def __init__(self, repository: StudySessionRepository):
        super().__init__(repository=repository)

    def log_session(self, *, user: User, validated_data: dict):
        event_data = {"strategy": validated_data["strategy"]}
        items_data = validated_data["items"]
        return self.log_event(user=user, event_data=event_data, items_data=items_data)

    def validate_event_against_profile(self, user: User, items_data: list[dict]) -> list[str]:
        warnings = []
        profile = getattr(user, "study_profile", None)

        if profile and profile.focus_limit_minutes:
            total_session_time = sum(item.get("time_minutes", 0) for item in items_data)
            if total_session_time > profile.focus_limit_minutes:
                warnings.append(
                    f"Atenção: A duração desta sessão ({total_session_time} min) excede o seu "
                    f"limite de foco contínuo ({profile.focus_limit_minutes} min). Faça pausas."
                )
        return warnings
