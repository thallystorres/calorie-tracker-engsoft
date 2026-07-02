from django.contrib.auth.models import User
from rest_framework.exceptions import NotFound
from core.profiles.services import BaseProfileService
from .models import StudyProfile
from .repositories import StudyProfileRepository

def get_profile_or_404(user: User) -> StudyProfile:
    try:
        return user.study_profile
    except StudyProfile.DoesNotExist:
        raise NotFound("Perfil de estudos não encontrado.") from None

class StudyProfileService(BaseProfileService):
    def __init__(self, repository: StudyProfileRepository):
        self.repo = repository

    def calculate_custom_targets(self, profile: StudyProfile) -> None:
        profile.target_weekly_minutes = profile.weekly_availability_hours * 60

        if profile.goal == StudyProfile.GoalChoices.CONCURSO:
            profile.target_recall_rate = 85.00
            profile.target_quiz_score = 90.00
        elif profile.goal == StudyProfile.GoalChoices.IDIOMA:
            profile.target_recall_rate = 90.00
            profile.target_quiz_score = 75.00
        else:
            profile.target_recall_rate = 70.00
            profile.target_quiz_score = 70.00
