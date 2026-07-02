from abc import ABC, abstractmethod

from django.contrib.auth.models import User
from django.db import transaction

from .models import BaseTrackedEvent


class BaseTrackerService(ABC):
    def __init__(self, repository):
        self._repo = repository

    @transaction.atomic
    def log_event(
        self, user: User, event_data: dict, items_data: list[dict]
    ) -> tuple[BaseTrackedEvent, list[str]]:

        warnings = self.validate_event_against_profile(user, items_data)

        event = self._repo.create_event(user=user, **event_data)

        self._repo.create_items(event=event, items_data=items_data)

        return event, warnings

    @abstractmethod
    def validate_event_against_profile(
        self, user: User, items_data: list[dict]
    ) -> list[str]:
        """
        Hook para as regras de negócio.
        - CalorIA: Procura por Alérgenos/Restrições.
        - AcademIA: Procura por sobrecarga em algum grupamento muscular.
        - EstudaAI: Confere se o tempo de estudo excede o limite de foco do Usuário.
        """
        pass
