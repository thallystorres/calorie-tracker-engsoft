from datetime import timedelta

from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone

from apps.profiles.restrictions import extract_user_restriction_codes
from apps.tracker.dependencies import get_meal_repository

from ..exceptions import ProfileRequiredError


class ContextBuilder:
    def __init__(self, user: User | None = None):
        self.user = user
        self.context = {}

    def add_profile_data(self):
        repo = get_meal_repository()
        if not self.user:
            return self

        profile = getattr(self.user, "nutritional_profile", None)
        if profile is None:
            raise ProfileRequiredError(
                "Preencha seu perfil nutricional antes de pedir sugestões."
            )

        hoje = timezone.now().replace(hour=0, minute=0, second=0)
        itens_hoje = repo.get_meal_items_for_user_from_date(self.user, hoje)
        calorias_consumidas = (
            itens_hoje.aggregate(total=Sum("kcal_total"))["total"] or 0
        )
        calorias_restantes = float(profile.daily_calorie_target) - float(
            calorias_consumidas
        )

        self.context["calorias_restantes"] = max(0, calorias_restantes)
        self.context["objetivo"] = profile.get_goal_display()
        # TODO: Rastrear o Consumo de macros
        self.context["macros_consumidos"] = {
            "carb": 150,
            "protein": 80,
            "fat": 40,
        }  # Mock temporário (pelo amor de deus alguem lembra de implementar isso depois)
        return self

    def add_history(self):
        repo = get_meal_repository()
        if not self.user:
            return self

        meals_manager = getattr(self.user, "meals", None)
        first_meal = (
            meals_manager.order_by("eaten_at").first()
            if meals_manager is not None
            else None
        )
        historico_insuficiente = (
            not first_meal or (timezone.now() - first_meal.eaten_at).days < 7
        )

        sete_dias_atras = timezone.now() - timedelta(days=7)
        itens_historico = repo.get_meal_items_for_user_from_date(
            self.user, sete_dias_atras
        )
        alimentos_frequentes = list(
            itens_historico.values_list("food__name", flat=True).distinct()[:10]
        )

        self.context["historico_refeicoes"] = (
            ", ".join(alimentos_frequentes)
            if alimentos_frequentes
            else "Nenhum dado prévio registrado."
        )
        self.context["historico_insuficiente"] = historico_insuficiente
        return self

    def add_restrictions(self):
        if not self.user:
            return self

        restricoes = sorted(extract_user_restriction_codes(self.user))
        self.context["restricoes"] = ", ".join(restricoes) if restricoes else "Nenhuma"
        return self

    def add_saved_contents(self, saved_contents: list[str]):
        self.context["texto_consolidado"] = "\n\n--- PRÓXIMO ITEM ---\n\n".join(
            saved_contents
        )
        return self

    def build(self) -> dict:
        return self.context
