import os
import time
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any

import openfoodfacts
from django.core.management.base import BaseCommand

from apps.foods.allergens import normalize_openfoodfacts_allergens
from apps.foods.models import Food


class Command(BaseCommand):
    help = "Importa milhares de alimentos usando a SDK oficial do Open Food Facts"

    def handle(self, *args, **kwargs):
        self.stdout.write(
            self.style.SUCCESS("A iniciar a importação via SDK oficial...")
        )

        cookie_sessao = os.getenv("OFF_SESSION_COOKIE")

        api = openfoodfacts.API(
            user_agent="CalorAI_EngSoft_Project/1.0",
            country=openfoodfacts.Country.br,
            session_cookie=cookie_sessao,
        )

        termos_busca = [
            "arroz",
            "feijão",
            "frango",
            "leite",
            "pão",
            "ovo",
            "carne",
            "peixe",
            "macarrão",
            "queijo",
            "manteiga",
            "azeite",
            "aveia",
            "iogurte",
            "batata",
            "cenoura",
            "banana",
            "maçã",
            "café",
            "açúcar",
            "tapioca",
            "suco",
            "biscoito",
            "presunto",
            "atum",
            "salsicha",
            "creme de leite",
            "leite condensado",
            "farinha",
            "chocolate",
            "amendoim",
            "azeitona",
            "milho",
            "tomate",
            "cebola",
        ]

        importados = 0
        produtos_por_pagina = 100
        paginas_por_termo = 3

        for termo in termos_busca:
            self.stdout.write(f"\n--- A pesquisar por: {termo} ---")

            for pagina in range(1, paginas_por_termo + 1):
                try:
                    self.stdout.write(f"A descarregar página {pagina}...")

                    resultados = api.product.text_search(
                        query=termo, page=pagina, page_size=produtos_por_pagina
                    )

                    produtos = resultados.get("products", [])

                    if not produtos:
                        break

                    for item in produtos:
                        nome = item.get("product_name_pt") or item.get("product_name")
                        if not nome or "nutriments" not in item:
                            continue

                        nutrientes = item["nutriments"]
                        kcal = nutrientes.get("energy-kcal_100g", 0)

                        if kcal <= 0:
                            continue

                        proteina = nutrientes.get("proteins_100g", 0)
                        carbos = nutrientes.get("carbohydrates_100g", 0)
                        gordura = nutrientes.get("fat_100g", 0)
                        fibra = nutrientes.get("fiber_100g", 0)

                        alergios_limpos = normalize_openfoodfacts_allergens(item)

                        _, created = Food.objects.get_or_create(
                            name=nome[:255],
                            defaults={
                                "kcal_per_100g": self._to_decimal(kcal),
                                "protein_per_100g": self._to_decimal(proteina),
                                "carbs_per_100g": self._to_decimal(carbos),
                                "fat_per_100g": self._to_decimal(gordura),
                                "fiber_per_100g": self._to_decimal(fibra),
                                "source": Food.FoodSource.OFF,
                                "allergens": alergios_limpos,
                            },
                        )
                        if created:
                            importados += 1

                    time.sleep(1)

                except Exception as e:  # noqa: BLE001
                    self.stdout.write(
                        self.style.WARNING(f"Erro na página {pagina} de '{termo}': {e}")
                    )
                    break

        self.stdout.write(
            self.style.SUCCESS(
                f"\nImportação concluída! {importados} novos alimentos adicionados."
            )
        )

    def _to_decimal(self, value: Any) -> Decimal:
        try:
            return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        except (InvalidOperation, TypeError, ValueError):
            return Decimal("0.00")
