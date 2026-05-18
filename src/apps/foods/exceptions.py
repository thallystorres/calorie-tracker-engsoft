from core.exceptions import AppError


class EmbeddingError(AppError):
    default_detail = "Falha ao gerar embedding do alimento."
    default_code = "embedding_error"
    default_status = 502


class FoodImportError(AppError):
    default_detail = "Falha ao importar alimento."
    default_code = "food_import_error"
    default_status = 502
