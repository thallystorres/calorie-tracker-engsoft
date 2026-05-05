from decimal import Decimal

from django.contrib.auth.models import User

from .models import FoodRestriction, NutritionalProfile
from .repositories import NutritionalProfileRepository


class ProfileService:
    def __init__(self, repository: NutritionalProfileRepository):
        self.repo = repository

    def calculate_bmr(
        self, weight: Decimal, height: int, age: int, sex: str
    ) -> Decimal:
        bmr = (10 * weight) + (Decimal("6.25") * height) - (5 * age)
        if sex == "M":
            bmr += Decimal(5)
        elif sex == "F":
            bmr -= Decimal(161)
        else:
            msg = f"Sexo '{sex}' inválido. Esperado: 'M' ou 'F'."
            raise ValueError(msg)

        return bmr.quantize(Decimal("0.01"))

    def calculate_daily_target(
        self, bmr: Decimal, activity_level: str, goal: str
    ) -> Decimal:

        # Total Daily Expenditure
        tdee = bmr
        match activity_level:
            case "SEDENTARIO":
                tdee *= Decimal("1.2")
            case "LEVE":
                tdee *= Decimal("1.375")
            case "MODERADA":
                tdee *= Decimal("1.55")
            case "ALTA":
                tdee *= Decimal("1.725")
            case "MUITO_ALTA":
                tdee *= Decimal("1.9")
            case _:
                msg = (
                    f"activity_level '{activity_level}' inválido."
                    " Esperado: 'SEDENTARIO', 'LEVE', 'MODERADA', 'ALTA' ou 'MUITO ALTA'"
                )
                raise ValueError(msg)

        daily_target = tdee
        match goal:
            case "PERDA":
                daily_target -= Decimal(500)
            case "MANUTENCAO":
                pass  # Nao precisa nem de deficit nem superavit
            case "GANHO":
                daily_target += Decimal(300)
            case _:
                msg = (
                    f"goal '{goal}' inválida. Esperado: 'PERDA', 'MANUTENCAO', 'GANHO'"
                )
                raise ValueError(msg)

        return daily_target.quantize(Decimal("0.01"))

    def upsert_profile(
        self, profile: NutritionalProfile, data: dict
    ) -> NutritionalProfile:
        for attr, value in data.items():
            setattr(profile, attr, value)

        profile.bmr = self.calculate_bmr(
            profile.weight_kg, profile.height_cm, profile.age, profile.sex
        )

        profile.daily_calorie_target = self.calculate_daily_target(
            profile.bmr, profile.activity_level, profile.goal
        )

        profile.save()
        return profile

    def replace_restrictions(
        self, *, profile: NutritionalProfile, restrictions_data: list[dict]
    ) -> None:
        FoodRestriction.objects.filter(profile=profile).delete()

        new_items = [
            FoodRestriction(profile=profile, **item) for item in restrictions_data
        ]
        if new_items:
            FoodRestriction.objects.bulk_create(new_items)

    def extract_user_restriction_codes(self, user: User) -> set[str]:
        profile = getattr(user, "nutritional_profile", None)
        if profile is None:
            return set()
        return self._extract_profile_restriction_codes(profile)

    def _extract_profile_restriction_codes(
        self, profile: NutritionalProfile
    ) -> set[str]:
        restriction_codes: set[str] = set()

        restriction_items = getattr(profile, "restriction_items", None)
        if restriction_items is not None and hasattr(restriction_items, "values_list"):
            restriction_codes.update(
                value
                for value in restriction_items.values_list(
                    "restriction_type", flat=True
                )
                if value
            )

        return restriction_codes
