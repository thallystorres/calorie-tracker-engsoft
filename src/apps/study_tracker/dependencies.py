from .services import StudyTrackerService
from .repositories import StudySessionRepository

def get_study_tracker_service() -> StudyTrackerService:
    repository = StudySessionRepository()
    return StudyTrackerService(repository)

def get_study_session_repository() -> StudySessionRepository:
    return StudySessionRepository()
