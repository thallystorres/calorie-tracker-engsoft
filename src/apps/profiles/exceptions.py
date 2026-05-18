from core.exceptions import AppError


class InvalidProfileDataError(AppError):
    default_detail = "Dado de perfil inválido."
    default_code = "invalid_profile_data"
    default_status = 422
