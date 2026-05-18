from core.exceptions import AppError


class TaskError(AppError):
    default_detail = "Erro na execução de tarefa em segundo plano."
    default_code = "task_error"
    default_status = 500
