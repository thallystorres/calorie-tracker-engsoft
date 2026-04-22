from datetime import timedelta

from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone

from apps.tracker.models import MealItem

from ..exceptions import ProfileRequiredError


class ContextBuilderService:
    def get_user_context(self, user: User) -> dict:
        if not hasattr(user, "nutritional_profile"):
            raise ProfileRequiredError(
                "Preencha seu perfil nutricional antes de pedir sugestões."
            )

        profile = user.nutritional_profile

        # Identifica se o usuário tem menos de 7 dias de uso
        first_meal = user.meals.order_by("eaten_at").first()
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

        restricoes = list(
            profile.dietary_restrictions.values_list("restriction_type", flat=True)
        )

        return {
            "calorias_restantes": max(0, calorias_restantes),
            "restricoes": ", ".join(restricoes) if restricoes else "Nenhuma",
            # Fallback caso a lista esteja vazia
            "historico_refeicoes": ", ".join(alimentos_frequentes)
            if alimentos_frequentes
            else "Nenhum dado prévio registrado.",
            "macros_consumidos": {"carb": 150, "protein": 80, "fat": 40},
            "historico_insuficiente": historico_insuficiente,  # Passando a flag para o serviço
        }
