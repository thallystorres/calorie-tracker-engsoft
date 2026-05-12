from typing import Any

from pgvector.django import L2Distance

from .models import Food


class FoodRepository:
    def list_foods(self, *, query: str | None = None):
        qs = Food.objects.all().order_by("name")

        if query:
            qs = qs.filter(name__icontains=query)

        return qs

    def get_by_id(self, food_id: int) -> Food | None:
        return Food.objects.filter(id=food_id).first()

    def create_food(self, *, validated_data: dict[str, Any]) -> Food:
        return Food.objects.create(**validated_data)

    def exists_by_name(self, name: str) -> bool:
        return Food.objects.filter(name__iexact=name).exists()

    def search_semantic(self, embedding: list[float], limit: int = 5):
        """
        Busca alimentos semanticamente similares usando distância L2.
        """
        return (
            Food.objects.annotate(distance=L2Distance("embedding", embedding))
            .order_by("distance")[:limit]
        )
