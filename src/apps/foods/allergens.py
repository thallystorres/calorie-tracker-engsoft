from __future__ import annotations

import unicodedata
from collections.abc import Iterable
from typing import Any

# Canonical internal allergen tokens shared across food import and profile restrictions.
GLUTEN = "GLUTEN"
SOY = "SOY"
MILK = "MILK"
LACTOSE = "LACTOSE"
EGG = "EGG"
PEANUT = "PEANUT"
TREE_NUT = "TREE_NUT"
SEAFOOD = "SEAFOOD"
OATS = "OATS"

_RESTRICTION_TO_ALLERGENS = {
    "CELIACO": {GLUTEN},
    "INTOLERANTE_A_LACTOSE": {LACTOSE, MILK},
    "ALERGICO_OVO": {EGG},
    "FRUTOS_DO_MAR": {SEAFOOD},
    "AMENDOIM": {PEANUT},
    "SOJA": {SOY},
    "AVEIA": {OATS},
}

_ALLERGEN_SYNONYMS = {
    "en:gluten": GLUTEN,
    "gluten": GLUTEN,
    "glutenes": GLUTEN,
    "gluteno": GLUTEN,
    "glutenfree": GLUTEN,
    "trigo": GLUTEN,
    "wheat": GLUTEN,
    "centeio": GLUTEN,
    "cevada": GLUTEN,
    "en:soybeans": SOY,
    "en:soybean": SOY,
    "en:soya": SOY,
    "en:soya-lecithin": SOY,
    "soja": SOY,
    "soy": SOY,
    "soybean": SOY,
    "lecitinasoja": SOY,
    "en:milk": MILK,
    "leite": MILK,
    "milk": MILK,
    "en:lactose": LACTOSE,
    "lactose": LACTOSE,
    "en:eggs": EGG,
    "en:egg": EGG,
    "ovo": EGG,
    "ovos": EGG,
    "egg": EGG,
    "eggs": EGG,
    "en:peanuts": PEANUT,
    "en:peanut": PEANUT,
    "amendoim": PEANUT,
    "peanut": PEANUT,
    "peanuts": PEANUT,
    "en:nuts": TREE_NUT,
    "castanhas": TREE_NUT,
    "castanha": TREE_NUT,
    "nuts": TREE_NUT,
    "en:fish": SEAFOOD,
    "en:crustaceans": SEAFOOD,
    "en:molluscs": SEAFOOD,
    "frutosdomar": SEAFOOD,
    "seafood": SEAFOOD,
    "peixe": SEAFOOD,
    "en:oats": OATS,
    "aveia": OATS,
    "oats": OATS,
}


def _strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _normalize_token(value: str) -> str:
    cleaned = _strip_accents(value).lower().strip()
    return "".join(char for char in cleaned if char.isalnum() or char in {":", "_"})


def _iter_tokens(value: Any) -> Iterable[str]:
    if value is None:
        return

    if isinstance(value, str):
        raw_parts = value.replace(";", ",").split(",")
        for raw in raw_parts:
            token = raw.strip()
            if token:
                yield token
        return

    if isinstance(value, Iterable):
        for item in value:
            if isinstance(item, str):
                token = item.strip()
                if token:
                    yield token
        return


def normalize_food_allergens(raw_values: Iterable[Any] | None) -> list[str]:
    if not raw_values:
        return []

    normalized: set[str] = set()
    for raw_value in raw_values:
        for token in _iter_tokens(raw_value):
            canonical = _ALLERGEN_SYNONYMS.get(_normalize_token(token))
            if canonical:
                normalized.add(canonical)

    return sorted(normalized)


def normalize_openfoodfacts_allergens(product: dict[str, Any]) -> list[str]:
    raw_values: list[Any] = [
        product.get("allergens_tags", []),
        product.get("allergens", ""),
        product.get("allergens_from_ingredients", ""),
    ]
    return normalize_food_allergens(raw_values)


def normalize_profile_restrictions(restriction_codes: Iterable[str]) -> set[str]:
    mapped: set[str] = set()
    for code in restriction_codes:
        mapped.update(_RESTRICTION_TO_ALLERGENS.get(str(code).strip().upper(), set()))
    return mapped
