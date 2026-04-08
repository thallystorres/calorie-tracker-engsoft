from decimal import Decimal
from django.test import TestCase
from apps.profiles.services import ProfileService

class ProfileServiceTests(TestCase):
    def setUp(self):
        self.service = ProfileService(repository=None)

    def test_calculate_bmr_for_male(self):
        # Peso: 80kg, Altura: 180cm, Idade: 30 anos
        result = self.service.calculate_bmr(Decimal("80"), 180, 30, "M")

        self.assertEqual(result, Decimal("1780.00"))

    def test_calculate_bmr_raises_error_for_invalid_sex(self):
        with self.assertRaises(ValueError):
            self.service.calculate_bmr(Decimal("80"), 180, 30, "X")
