from typing import Any
from rest_framework.exceptions import NotFound, ValidationError
from .models import StudyContent
from .repositories import ContentRepository

class ContentService:
    def __init__(self, content_repository: ContentRepository):
        self._repo = content_repository

    def list_contents(self, *, query: str | None = None):
        return self._repo.list_contents(query=query)

    def get_content_or_404(self, *, content_id: int) -> StudyContent:
        content = self._repo.get_by_id(content_id=content_id)
        if content is None:
            raise NotFound("Conteúdo não encontrado.")
        return content

    def create_content(self, *, validated_data: dict[str, Any]) -> StudyContent:
        validated_data["source"] = StudyContent.ContentSource.MANUAL
        if self._repo.exists_by_name(validated_data["name"]):
            raise ValidationError("Um conteúdo com esse nome já existe.")
        return self._repo.create_content(validated_data=validated_data)
