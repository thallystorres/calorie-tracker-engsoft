from decimal import Decimal

from apps.foods.dependencies import get_food_repository
from apps.profiles.dependencies import get_profile_repository


def search_food(query: str, limite: int = 15) -> str:
    """Busca alimentos no banco de dados usando busca semântica. 
    DICA: Você pode passar múltiplos termos separados por vírgula (ex: 'arroz, feijão, frango') para buscar tudo de uma vez.
    """
    from apps.ai_engine.dependencies import get_gemini_client

    repo = get_food_repository()
    client = get_gemini_client()

    # Divide a query por vírgulas para suportar buscas múltiplas em uma única chamada
    terms = [t.strip() for t in query.split(",") if t.strip()]
    all_results = []
    seen_ids = set()

    for term in terms:
        try:
            # Gera o embedding da consulta com o prefixo recomendado para busca
            query_embedding = client.get_embedding(term, task_type="search_query")
            alimentos = repo.search_semantic(query_embedding, limit=limite)
        except Exception:
            # Fallback para busca por texto se o embedding falhar
            alimentos = repo.list_foods(query=term)[:limite]

        for a in alimentos:
            if a.id not in seen_ids:
                all_results.append(f"- {a.name} (ID: {a.id}): {a.kcal_per_100g} kcal/100g")
                seen_ids.add(a.id)

    if not all_results:
        return (
            f"Nenhum alimento encontrado com os termos '{query}'. Tente outros sinônimos."
        )

    return "\n".join(all_results)


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
