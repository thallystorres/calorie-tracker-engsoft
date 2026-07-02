from apps.academia.repositories import WorkoutRepository
from core.ai.services import GeminiLLMClient


def search_exercises_in_catalog(query: str, limit: int = 5) -> list[dict]:
    client = GeminiLLMClient()
    embedding = client.get_embedding(query, task_type="search_query")
    repo = WorkoutRepository()
    exercises = repo.search_exercises_semantic(embedding, limit=limit)
    return [
        {"id": ex.id, "name": ex.name, "muscle_group": ex.muscle_group}
        for ex in exercises
    ]
