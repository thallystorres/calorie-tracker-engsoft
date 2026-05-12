from datetime import timedelta

from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils import timezone

from apps.profiles.dependencies import get_profile_service
from apps.tracker.dependencies import get_meal_repository

from ..exceptions import ProfileRequiredError


class ContextBuilder:
    def __init__(self, user: User | None = None):
        self.user = user
        self.context = {}

    def add_profile_data(self):
        if not self.user:
            return self

        profile = getattr(self.user, "nutritional_profile", None)
        if profile is None:
            raise ProfileRequiredError(
                "Preencha seu perfil nutricional antes de pedir sugestões."
            )

        # Dados biográficos e metas estáticas
        perfil_bio = (
            f"Objetivo: {profile.get_goal_display()}. "
            f"Meta Diária: {profile.daily_calorie_target} kcal. "
            f"Idade: {profile.age} anos. "
            f"Peso: {profile.weight_kg} kg. "
            f"Altura: {profile.height_cm} cm. "
            f"Nível de Atividade: {profile.get_activity_level_display()}."
        )

        self.context["perfil_bio"] = perfil_bio
        self.context["objetivo"] = profile.get_goal_display()
        self.context["meta_kcal"] = float(profile.daily_calorie_target)

        return self

    def add_daily_progress(self):
        repo = get_meal_repository()
        if not self.user:
            return self

        profile = getattr(self.user, "nutritional_profile", None)
        if profile is None:
            return self

        hoje = timezone.localdate()
        totals = repo.get_daily_totals(self.user, hoje)
        itens_hoje = repo.get_meal_items_for_user_from_date(self.user, hoje)

        calorias_consumidas = (
            itens_hoje.aggregate(total=Sum("kcal_total"))["total"] or 0
        )
        calorias_restantes = float(profile.daily_calorie_target) - float(
            calorias_consumidas
        )

        self.context["calorias_consumidas"] = float(calorias_consumidas)
        self.context["calorias_restantes"] = max(0, calorias_restantes)
        self.context["macros_consumidos"] = {
            "carbs": float(totals.get("carbs") or 0),
            "protein": float(totals.get("protein") or 0),
            "fat": float(totals.get("fat") or 0),
            "fiber": float(totals.get("fiber") or 0),
        }

        return self

    def add_history(self):
        repo = get_meal_repository()
        if not self.user:
            return self

        hoje = timezone.localdate()
        sete_dias_atras = hoje - timedelta(days=7)

        meals_manager = getattr(self.user, "meals", None)
        first_meal = (
            meals_manager.order_by("eaten_at").first()
            if meals_manager is not None
            else None
        )

        itens_historico = repo.get_meal_items_for_user_from_date(
            self.user, sete_dias_atras
        )

        dias_com_refeicao = repo.count_days_with_meal_from_date(
            self.user, sete_dias_atras
        )
        historico_insuficiente = dias_com_refeicao < 4

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

        restricoes = sorted(
            get_profile_service().extract_user_restriction_codes(self.user)
        )
        self.context["restricoes"] = ", ".join(restricoes) if restricoes else "Nenhuma"
        return self

    def add_saved_contents(self, saved_contents: list[str]):
        self.context["texto_consolidado"] = "\n\n--- PRÓXIMO ITEM ---\n\n".join(
            saved_contents
        )
        return self

    def build(self) -> dict:
        return self.context
