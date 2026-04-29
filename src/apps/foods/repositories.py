from typing import Any

# from django.db.models import QuerySet
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
