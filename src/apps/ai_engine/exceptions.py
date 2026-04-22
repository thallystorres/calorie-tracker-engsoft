class AIEngineError(Exception):
    """Exceção base para o módulo de IA."""

    pass


class LLMAPIKeyNotSetError(AIEngineError):
    """Lançada quando a chave da API do LLM não está configurada."""

    pass


class ProfileRequiredError(AIEngineError):
    """Lançada quando o usuário tenta usar IA sem ter um Perfil Nutricional."""

    pass


class InsufficientDataError(AIEngineError):
    """Lançada quando o usuário não possui os 7 dias mínimos de histórico (RN08)."""

    pass
