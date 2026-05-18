from __future__ import annotations


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
