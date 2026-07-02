from abc import ABC, abstractmethod

from .models import BaseProfile


class BaseProfileService(ABC):
    def upsert_profile(self, profile: BaseProfile, data: dict) -> BaseProfile:
        for attr, value in data.items():
            setattr(profile, attr, value)

        self.calculate_custom_targets(profile)

        profile.save()
        return profile

    @abstractmethod
    def calculate_custom_targets(self, profile: BaseProfile) -> None:
        """
        To be implemented by the specific application.
        - CalorIA: Calculates BMR and Daily Calorie Target.
        - AcademIA: Calculates Weekly Workout Volume targets.
        - EstudaAI: Calculates Weekly Study Hour goals.
        """
        pass
