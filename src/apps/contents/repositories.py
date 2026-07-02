from typing import Any
from pgvector.django import L2Distance
from .models import StudyContent

class ContentRepository:
    def list_contents(self, *, query: str | None = None):
        qs = StudyContent.objects.all().order_by("name")
        if query:
            qs = qs.filter(name__icontains=query)
        return qs

    def get_by_id(self, content_id: int) -> StudyContent | None:
        return StudyContent.objects.filter(id=content_id).first()

    def create_content(self, *, validated_data: dict[str, Any]) -> StudyContent:
        return StudyContent.objects.create(**validated_data)

    def exists_by_name(self, name: str) -> bool:
        return StudyContent.objects.filter(name__iexact=name).exists()

    def search_semantic(self, embedding: list[float], limit: int = 5):
        return (
            StudyContent.objects.annotate(distance=L2Distance("embedding", embedding))
            .order_by("distance")[:limit]
        )
