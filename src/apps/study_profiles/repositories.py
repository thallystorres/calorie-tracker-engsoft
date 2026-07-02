from django.contrib.auth.models import User
from core.repositories import BaseRepository
from .models import StudyProfile, SavedSummary, SavedFlashcardSet, SavedQuiz

class StudyProfileRepository(BaseRepository[StudyProfile]):
    def __init__(self):
        super().__init__(StudyProfile)

    def create_summary(self, user: User, title: str, content: str) -> SavedSummary:
        return SavedSummary.objects.create(user=user, title=title, content=content)

    def create_flashcard_set(self, user: User, title: str, content: str) -> SavedFlashcardSet:
        return SavedFlashcardSet.objects.create(user=user, title=title, content=content)

    def create_quiz(self, user: User, title: str, content: str) -> SavedQuiz:
        return SavedQuiz.objects.create(user=user, title=title, content=content)
