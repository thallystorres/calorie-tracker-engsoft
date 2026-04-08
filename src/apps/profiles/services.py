from decimal import Decimal

from .models import NutritionalProfile
from .repositories import ProfileRepository


class ProfileService:
    def __init__(self, repository: ProfileRepository):
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
                msg = f"goal '{goal}' inválida. Esperado: 'PERDA', 'MANUTENCAO', 'GANHO'"
                raise ValueError(msg)

        return daily_target.quantize(Decimal("0.01"))

    def calculate_and_save_targets(
        self, profile: NutritionalProfile
    ) -> NutritionalProfile:
        bmr = self.calculate_bmr(
            profile.weight_kg, profile.height_cm, profile.age, profile.sex
        )

        daily_target = self.calculate_daily_target(
            bmr, profile.activity_level, profile.goal
        )

        return self.repo.update_targets(profile, bmr, daily_target)
