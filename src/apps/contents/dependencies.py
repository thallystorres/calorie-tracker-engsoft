from .services import ContentService
from .repositories import ContentRepository

def get_content_service() -> ContentService:
    repository = ContentRepository()
    return ContentService(content_repository=repository)

def get_content_repository() -> ContentRepository:
    return ContentRepository()
