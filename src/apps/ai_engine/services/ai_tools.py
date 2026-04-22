from decimal import Decimal

from apps.foods.models import Food
from apps.profiles.models import NutritionalProfile


def search_food(query: str) -> str:
    """
    Busca alimentos no banco de dados nutricional.
    Retorna o nome do alimento, calorias e macronutrientes por 100g.
    Sempre use esta ferramenta antes de sugerir um ingrediente para garantir que ele exista.
    """
    foods = Food.objects.filter(name__icontains=query)[:5]
    if not foods:
        return "Nenhum alimento encontrado. Tente buscar por sinônimos ou ingredientes mais básicos."

    results = []
    for f in foods:
        results.append(
            f"Nome: {f.name} | kcal/100g: {f.kcal_per_100g} | "
            f"Proteína: {f.protein_per_100g}g | Carboidratos: {f.carbs_per_100g}g | Gordura: {f.fat_per_100g}g"
        )
    return "\n".join(results)


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
