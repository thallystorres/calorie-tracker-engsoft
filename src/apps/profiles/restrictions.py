from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.contrib.auth.models import User


def _extract_legacy_restrictions(legacy_restrictions: object) -> set[str]:
    extracted: set[str] = set()
    if not isinstance(legacy_restrictions, list):
        return extracted

    for value in legacy_restrictions:
        if isinstance(value, str) and value:
            extracted.add(value)
            continue

        if isinstance(value, dict):
            code = value.get("restriction_type") or value.get("type")
            if code:
                extracted.add(str(code))

    return extracted


def extract_profile_restriction_codes(profile: object) -> set[str]:
    restriction_codes: set[str] = set()

    restriction_items = getattr(profile, "restriction_items", None)
    if restriction_items is not None and hasattr(restriction_items, "values_list"):
        restriction_codes.update(
            value
            for value in restriction_items.values_list("restriction_type", flat=True)
            if value
        )

    restriction_codes.update(
        _extract_legacy_restrictions(getattr(profile, "dietary_restrictions", None))
    )
    return restriction_codes


def extract_user_restriction_codes(user: User) -> set[str]:
    profile = getattr(user, "nutritional_profile", None)
    if profile is None:
        return set()
    return extract_profile_restriction_codes(profile)
