from apps.smarttracker_fw.core.repositories import BaseRepository

from .models import NutritionalProfile, SavedDiet, SavedRecipe, WeeklyPlan


class NutritionalProfileRepository(BaseRepository[NutritionalProfile]):
    def __init__(self):
        super().__init__(NutritionalProfile)

    def create_diet(self, user: User, title: str, content: str) -> SavedDiet:
        return SavedDiet.objects.create(user=user, title=title, content=content)
