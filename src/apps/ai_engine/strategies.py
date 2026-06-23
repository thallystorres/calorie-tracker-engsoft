from abc import ABC, abstractmethod
from typing import Any
from django.contrib.auth.models import User


class AIAssistantStrategy(ABC):
  """Interface abstrata para os Motores de IA do Framework (Padrão Strategy)"""

  @abstractmethod
  def generate_suggestion(self, user: User, prompt: str) -> dict[str, Any]:
    """Gera uma sugestão baseada no contexto do app implementado"""
    pass

  @abstractmethod
  def edit_content(self, current_content: str, instruction: str) -> str:
    """Permite à IA refinar uma sugestão previamente gerada"""
    pass
