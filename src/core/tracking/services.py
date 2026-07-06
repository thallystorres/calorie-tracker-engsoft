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


class BaseGoalService(ABC):
    def __init__(self, repository):
        self._repo = repository

    def get_active_goals(self, user):
        today = self.get_today()
        goals = list(
            self.get_goal_model().objects.filter(
                user=user, period_end__gte=today
            ).order_by("-created_at")
        )
        for goal in goals:
            current_value = self.get_current_value(user=user, goal=goal)
            is_achieved = self.is_goal_achieved(goal=goal, current_value=current_value)
            if goal.current_value != current_value or goal.is_achieved != is_achieved:
                goal.current_value = current_value
                goal.is_achieved = is_achieved
                goal.save(update_fields=["current_value", "is_achieved"])
        return goals

    def is_goal_achieved(self, goal, current_value):
        return self.is_target_achieved(
            target_value=goal.target_value,
            current_value=current_value,
        )

    def is_target_achieved(self, target_value, current_value):
        return target_value > 0 and current_value >= target_value

    @abstractmethod
    def get_today(self):
        pass

    @abstractmethod
    def get_goal_model(self):
        pass

    @abstractmethod
    def get_current_value(self, user, goal):
        pass
