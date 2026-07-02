from functools import cache

from core.ai.services import GeminiLLMClient

from .repositories import WorkoutRepository
from .services import GoalsService, VolumeMetricsService, WorkoutRoutineGeneratorService, WorkoutTrackerService


@cache
def get_workout_repository() -> WorkoutRepository:
    return WorkoutRepository()


@cache
def get_tracker_service() -> WorkoutTrackerService:
    return WorkoutTrackerService(workout_repository=get_workout_repository())


@cache
def get_volume_metrics_service() -> VolumeMetricsService:
    return VolumeMetricsService(workout_repository=get_workout_repository())


@cache
def get_goals_service() -> GoalsService:
    return GoalsService(workout_repository=get_workout_repository())


@cache
def get_routine_generator_service() -> WorkoutRoutineGeneratorService:
    return WorkoutRoutineGeneratorService(llm_client=GeminiLLMClient())
