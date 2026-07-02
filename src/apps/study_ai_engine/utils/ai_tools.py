import logging
from apps.contents.repositories import ContentRepository
from core.ai_engine.clients.gemini import GeminiLLMClient

logger = logging.getLogger(__name__)


def search_study_content(query: str, limit: int = 10) -> str:
  """Ferramenta (Tool) para a IA buscar tópicos na base de conhecimentos."""
  repo = ContentRepository()
  client = GeminiLLMClient()

  try:
    query_embedding = client.get_embedding(query, task_type="search_query")
    contents = repo.search_semantic(query_embedding, limit=limit)
  except Exception as e:
    logger.warning("Falha na busca semântica: %s. Fazendo fallback textual.", e)
    contents = repo.model.objects.filter(name__icontains=query)[:limit]

  if not contents:
    return f"Nenhum tópico encontrado para '{query}'."

  return "\n".join(
    [f"- {c.name} (Nível: {c.difficulty_level}, Categoria: {c.get_category_display()})" for c in contents])
