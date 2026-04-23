from django.contrib.auth.models import User

from apps.ai_engine.dependencies import get_meal_suggester_service
from apps.ai_engine.services.meal_suggester import MealSuggestionSchema


class DietAssistantService:
    def __init__(self):
        self._meal_suggester = get_meal_suggester_service()

    def _format_reply(self, suggestion: MealSuggestionSchema) -> str:
        lines: list[str] = [
            f"## {suggestion.meal_name}",
            f"Calorias estimadas: {suggestion.estimated_calories} kcal",
            "",
            "### Ingredientes",
        ]

        for item in suggestion.ingredients:
            lines.append(f"- {item.name}: {item.quantity_grams}g")

        if suggestion.target_adjustments.applied:
            lines.extend(
                [
                    "",
                    "### Ajuste de Meta",
                    suggestion.target_adjustments.description,
                ]
            )

        if suggestion.warning:
            lines.extend(["", f"**Nota:** {suggestion.warning}"])

        return "\n".join(lines)

    def generate_diet_suggestion(self, user: User, user_message: str = "") -> str:
        prompt = user_message.strip() or "Sugira uma refeição equilibrada para hoje."
        suggestion = self._meal_suggester.suggest_meal(user=user, user_prompt=prompt)
        return self._format_reply(suggestion)
