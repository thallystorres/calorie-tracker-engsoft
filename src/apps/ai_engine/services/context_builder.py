from datetime import timedelta
from typing import Any

from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone

from apps.profiles.restrictions import extract_user_restriction_codes
from apps.tracker.models import MealItem

from ..exceptions import ProfileRequiredError


class ContextBuilderService:
    def get_user_context(self, user: User) -> dict:
        profile = getattr(user, "nutritional_profile", None)
        if profile is None:
            msg = "Preencha seu perfil nutricional antes de pedir sugestões."
            raise ProfileRequiredError(msg)

        meals_manager: Any = getattr(user, "meals", None)

        # Identifica se o usuário tem menos de 7 dias de uso
        first_meal = (
            meals_manager.order_by("eaten_at").first()
            if meals_manager is not None
            else None
        )
        historico_insuficiente = (
            not first_meal or (timezone.now() - first_meal.eaten_at).days < 7
        )

        hoje = timezone.now().replace(hour=0, minute=0, second=0)

        itens_hoje = MealItem.objects.filter(meal__user=user, meal__eaten_at__gte=hoje)
        calorias_consumidas = (
            itens_hoje.aggregate(total=Sum("kcal_total"))["total"] or 0
        )
        calorias_restantes = float(profile.daily_calorie_target) - float(
            calorias_consumidas
        )

        sete_dias_atras = timezone.now() - timedelta(days=7)
        itens_historico = MealItem.objects.filter(
            meal__user=user, meal__eaten_at__gte=sete_dias_atras
        )
        alimentos_frequentes = list(
            itens_historico.values_list("food__name", flat=True).distinct()[:10]
        )

        restricoes = sorted(extract_user_restriction_codes(user))

        return {
            "calorias_restantes": max(0, calorias_restantes),
            "restricoes": ", ".join(restricoes) if restricoes else "Nenhuma",
            # Fallback caso a lista esteja vazia
            "historico_refeicoes": ", ".join(alimentos_frequentes)
            if alimentos_frequentes
            else "Nenhum dado prévio registrado.",
            "macros_consumidos": {"carb": 150, "protein": 80, "fat": 40},
            "historico_insuficiente": historico_insuficiente,
        }
