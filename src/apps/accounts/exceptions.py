from core.exceptions import AppError


class EmailSendError(AppError):
    default_detail = "Falha ao enviar e-mail."
    default_code = "email_send_error"
    default_status = 500
