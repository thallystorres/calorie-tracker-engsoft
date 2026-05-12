from decimal import Decimal

from apps.foods.dependencies import get_food_repository
from apps.profiles.dependencies import get_profile_repository


def search_food(query: str, limite: int = 5) -> str:
    """Busca alimentos no banco de dados usando busca semântica para encontrar os itens mais relevantes."""
    from apps.ai_engine.dependencies import get_gemini_client

    repo = get_food_repository()
    client = get_gemini_client()

    try:
        # Gera o embedding da consulta com o prefixo recomendado para busca
        query_embedding = client.get_embedding(query, task_type="search_query")
        alimentos = repo.search_semantic(query_embedding, limit=limite)
    except Exception:
        # Fallback para busca por texto se o embedding falhar
        alimentos = repo.list_foods(query=query)[:limite]

    if not alimentos:
        return (
            f"Nenhum alimento encontrado com o termo '{query}'. Tente outro sinônimo."
        )

    resultados = [f"- {a.name} (ID: {a.id}): {a.kcal_per_100g} kcal/100g" for a in alimentos]
    return "\n".join(resultados)


def adjust_future_targets(
    user_id: int, adjustment_type: str, kcal_impact: float, days: int
) -> str:
    """Ajusta a meta calórica do usuário."""
    repo = get_profile_repository()
    profile = repo.get_by_user_id(user_id)

    if not profile:
        return "Erro: Perfil nutricional não encontrado para este usuário."

    impact = Decimal(str(kcal_impact))
    new_target = profile.daily_calorie_target

    if adjustment_type.upper() == "REDUZIR":
        new_target -= impact
    elif adjustment_type.upper() == "AUMENTAR":
        new_target += impact

    repo.update_targets(profile=profile, bmr=profile.bmr, daily_target=new_target)
    return f"Meta calórica ajustada com sucesso em {kcal_impact} kcal pelos próximos {days} dias."
