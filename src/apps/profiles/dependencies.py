from functools import cache

from .repositories import NutritionalProfileRepository
from .services import ProfileService


@cache
def get_profile_service() -> ProfileService:
    return ProfileService(
        repository=NutritionalProfileRepository()
    )
