from functools import cache

from .repositories import WorkoutRepository
from .services import WorkoutTrackerService


@cache
def get_workout_repository() -> WorkoutRepository:
    return WorkoutRepository()


@cache
def get_tracker_service() -> WorkoutTrackerService:
    return WorkoutTrackerService(workout_repository=get_workout_repository())
