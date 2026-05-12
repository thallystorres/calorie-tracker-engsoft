from typing import Literal

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


class PlanIngredientSchema(BaseModel):
    name: str
    quantity_grams: float
    estimated_kcal: float


class PlanMealSchema(BaseModel):
    label: str = Field(description="Ex: cafe, almoco, jantar, lanche")
    name: str = Field(description="Nome apetitoso do prato")
    ingredients: list[PlanIngredientSchema]
    total_kcal: float


class DailyPlanSchema(BaseModel):
    day_number: int = Field(description="1 a 7")
    meals: list[PlanMealSchema]
    daily_total_kcal: float


class WeeklyPlanSchema(BaseModel):
    days: list[DailyPlanSchema]
    weekly_average_kcal: float
    shopping_list_tips: list[str] = Field(
        description="Dicas gerais de compras para a semana"
    )


class AIPlannerResponseSchema(BaseModel):
    state: Literal["asking", "drafting"] = Field(
        description="Use 'asking' se precisar de mais detalhes do usuário. Use 'drafting' se tiver tudo para criar o plano."
    )
    message: str = Field(
        description="A sua resposta em texto para o usuário (perguntas ou explicação do plano)."
    )
    weekly_plan: WeeklyPlanSchema | None = Field(
        description="O plano semanal estruturado. Só preencha se state for 'drafting'."
    )
