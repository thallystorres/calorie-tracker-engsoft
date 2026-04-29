from pydantic import BaseModel, Field


class DietResponseSchema(BaseModel):
    tipo: str = Field(
        description="Classifique a resposta estritamente como 'dieta', 'receita' ou 'chat'"
    )
    texto: str = Field(
        description="A sua resposta redigida para o utilizador, formatada em Markdown limpo"
    )


class IngredientSchema(BaseModel):
    name: str
    quantity_grams: float


class TargetAdjustmentSchema(BaseModel):
    applied: bool
    description: str


class MealSuggestionSchema(BaseModel):
    meal_name: str
    ingredients: list[IngredientSchema]
    estimated_calories: float
    target_adjustments: TargetAdjustmentSchema
    warning: str | None = None
