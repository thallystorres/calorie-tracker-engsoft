from core.exceptions import AppError


class AppError(Exception):
    """Exceção Base para erros a nível de aplicação"""

    default_detail = "Ocorreu um erro inesperado."
    default_code = "error"
    default_status = 400

    def __init__(
        self,
        detail: str | None = None,
        code: str | None = None,
        status: int | None = None,
    ):
        self.detail = detail or self.default_detail
        self.code = code or self.default_code
        self.status = status or self.default_status
        super().__init__(self.detail)


class AIEngineError(AppError):
    """Exceção base para o módulo de IA."""

    default_detail = "Erro no motor de IA."
    default_code = "ai_engine_error"
    default_status = 400

    pass


class LLMAPIKeyNotSetError(AIEngineError):
    """Lançada quando a chave da API do LLM não está configurada."""

    default_detail = "Chave de API do modelo de IA não configurada."
    default_code = "llm_api_key_not_set"
    default_status = 503

    pass


class ProfileRequiredError(AIEngineError):
    """Lançada quando o usuário tenta usar IA sem ter um Perfil Nutricional."""

    default_detail = "Preencha seu perfil nutricional antes de pedir sugestões."
    default_code = "profile_required"
    default_status = 400

    pass


class LLMRequestError(AIEngineError):
    """Lançada quando a requisição ao LLM falha (rede, timeout, API)."""

    default_detail = "Falha de comunicação com o modelo de IA."
    default_code = "llm_request_error"
    default_status = 502

    pass


class LLMResponseError(AIEngineError):
    """Lançada quando a resposta do LLM é inválida ou malformada."""

    default_detail = "Resposta inválida do modelo de IA."
    default_code = "llm_response_error"
    default_status = 502

    pass


class LLMAttemptsExhaustedError(AIEngineError):
    """Lançada após todas as tentativas de requisição ao LLM falharem."""

    default_detail = "O modelo de IA não respondeu após múltiplas tentativas."
    default_code = "llm_attempts_exhausted"
    default_status = 503

    pass


class EmailSendError(AppError):
    default_detail = "Falha ao enviar e-mail."
    default_code = "email_send_error"
    default_status = 500


class InvalidProfileDataError(AppError):
    default_detail = "Dado de perfil inválido."
    default_code = "invalid_profile_data"
    default_status = 422
