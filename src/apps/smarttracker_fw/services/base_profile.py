from abc import ABC, abstractmethod

from ..models import BaseProfile


class BaseProfileService(ABC):
    def upsert_profile(self, profile: BaseProfile, data: dict) -> BaseProfile:
        self.calculate_custom_targets(profile)
        profile.save()
        return profile

    @abstractmethod
    def calculate_custom_targets(self, profile: BaseProfile) -> None:
        """To be implemented by the specific application (e.g., CalorIA calculates BMR)."""
        pass
