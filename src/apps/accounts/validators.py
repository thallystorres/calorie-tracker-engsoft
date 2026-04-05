import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class StrongPasswordValidator:
    def __init__(self, min_length: int = 8) -> None:
        self.min_length = min_length

    def validate(self, password: str, user=None) -> None:
        errors: list[str] = []

        if len(password) < self.min_length:
            errors.append(
                _(f"A senha deve ter no mínimo {self.min_length} caracteres.")
            )
        if not re.search(r"[A-Z]", password):
            errors.append(_("A senha deve conter ao menos uma letra maiúscula,"))
        if not re.search(r"[a-z]", password):
            errors.append(_("A senha deve conter ao menos uma letra minúscula."))
        if not re.search(r"[0-9]", password):
            errors.append(_("A senha deve conter ao menos um número."))
        if not re.search(r"[^A-Za-z0-9]", password):
            errors.append(_("A senha deve conter ao menos 1 caractere especial."))

        if errors:
            raise ValidationError(errors)  # type: ignore

    def get_help_text(self) -> str:
        return _(
            f"Sua senha deve conter no mínimo {self.min_length} caracteres e incluir "
            "letra maiúscula, letra minúscula, número e caractere especial."
        )
