from decimal import Decimal

from apps.foods.models import Food
from apps.profiles.models import NutritionalProfile


def search_food(query: str, limite: int = 5) -> str:
    """
    Use esta ferramenta SEMPRE que precisar de sugerir um alimento.
    Passe um termo_pesquisa (ex: 'frango', 'arroz', 'leite').
    Retorna uma lista de alimentos disponíveis no sistema com as suas calorias.
    """
    alimentos = Food.objects.filter(name__icontains=query)[:limite]

    if not alimentos.exists():
        return (
            f"Nenhum alimento encontrado com o termo '{query}'. Tente outro sinônimo."
        )

    resultados = []
    for a in alimentos:
        resultados.append(f"- {a.name}: {a.kcal_per_100g} kcal/100g")

    return "\n".join(resultados)


def adjust_future_targets(
    user_id: int, adjustment_type: str, kcal_impact: float, days: int
) -> str:
    """
    (Experimental) Ajusta a meta calórica do usuário para os próximos dias.
    adjustment_type deve ser 'REDUZIR' ou 'AUMENTAR'.
    """
    try:
        profile = NutritionalProfile.objects.get(user__id=user_id)
        impact = Decimal(str(kcal_impact))

        if adjustment_type.upper() == "REDUZIR":
            profile.daily_calorie_target -= impact
        elif adjustment_type.upper() == "AUMENTAR":
            profile.daily_calorie_target += impact

        profile.save(update_fields=["daily_calorie_target"])
        return f"Meta calórica ajustada com sucesso em {kcal_impact} kcal pelos próximos {days} dias."
    except NutritionalProfile.DoesNotExist:
        return "Erro: Perfil nutricional não encontrado para este usuário."
