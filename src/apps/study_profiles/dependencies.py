from .services import StudyProfileService
from .repositories import StudyProfileRepository

def get_study_profile_service() -> StudyProfileService:
    repository = StudyProfileRepository()
    return StudyProfileService(repository)
