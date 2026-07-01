from abc import ABC, abstractmethod

from django.contrib.auth.models import User
from django.db import transaction

from ..models import BaseTrackedEvent


class BaseTrackerService(ABC):
    @transaction.atomic
    def log_event(
        self, user: User, event_data: dict, items_data: list[dict]
    ) -> tuple[BaseTrackedEvent, list[str]]:
        warnings = self.validate_event_against_profile(user, items_data)
        return event, warnings

    @abstractmethod
    def validate_event_against_profile(
        self, user: User, items_data: list[dict]
    ) -> list[str]:
        """Hook to check for things like Allergies, Over-training, etc."""
        pass
