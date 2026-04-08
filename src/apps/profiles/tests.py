from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.profiles.services import NutritionalProfile, ProfileService


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


class ProfileMeViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="Forte@1234",
            is_active=True,
        )
        self.url = reverse("profiles:me")

        self.valid_payload = {
            "weight_kg": "80.00",
            "height_cm": 180,
            "age": 30,
            "sex": "M",
            "activity_level": "SEDENTARIO",
            "goal": "PERDA",
        }

    def test_get_profile_unauthenticated_returns_403(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_get_profile_not_found_returns_404(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["detail"], "Perfil Nutricional não encontrado.")

    def test_get_profile_returns_200_and_data(self):
        self.client.force_login(self.user)
        NutritionalProfile.objects.create(
            user=self.user,
            weight_kg=Decimal("80.00"),
            height_cm=180,
            age=30,
            sex="M",
            activity_level="SEDENTARIO",
            goal="PERDA",
            bmr=Decimal("1780.00"),
            daily_calorie_target=Decimal("1636.00"),
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["weight_kg"], "80.00")
        self.assertEqual(response.data["bmr"], "1780.00")

    def test_put_profile_unauthenticated_returns_403(self):
        response = self.client.put(self.url, data=self.valid_payload, format="json")
        self.assertEqual(response.status_code, 403)

    def test_put_creates_new_profile_and_calculates_targets(self):
        self.client.force_login(self.user)

        response = self.client.put(self.url, data=self.valid_payload, format="json")

        self.assertEqual(response.status_code, 200)

        # Verificar que tudo foi calculado e salvo
        self.user.refresh_from_db()
        profile = self.user.nutritional_profile

        # BMR: (10*80) + (6.25*180) - (5*30) + 5 = 1780
        self.assertEqual(profile.bmr, Decimal("1780.00"))
        # TDEE (Sedentario): 1780 * 1.2 = 2136. Goal (Perda): 2136 - 500 = 1636
        self.assertEqual(profile.daily_calorie_target, Decimal("1636.00"))

        # Verificar formato de saída da API
        self.assertEqual(response.data["bmr"], "1780.00")
        self.assertEqual(response.data["daily_calorie_target"], "1636.00")

    def test_put_updates_existing_profile(self):
        self.client.force_login(self.user)

        # Profile inicial
        profile = NutritionalProfile.objects.create(
            user=self.user,
            weight_kg=Decimal("80.00"),
            height_cm=180,
            age=30,
            sex="M",
            activity_level="SEDENTARIO",
            goal="PERDA",
        )

        # Atualizar com novo peso e goal
        updated_payload = self.valid_payload.copy()
        updated_payload["weight_kg"] = "90.00"
        updated_payload["goal"] = "MANUTENCAO"

        response = self.client.put(self.url, data=updated_payload, format="json")

        self.assertEqual(response.status_code, 200)
        profile.refresh_from_db()

        self.assertEqual(profile.weight_kg, Decimal("90.00"))
        self.assertEqual(profile.goal, "MANUTENCAO")

        # BMR deveria ser recalculado: (10*90) + (6.25*180) - (5*30) + 5 = 1880
        self.assertEqual(profile.bmr, Decimal("1880.00"))
        # TDEE (Sedentario): 1880 * 1.2 = 2256. Goal (Manutencao) = 2256
        self.assertEqual(profile.daily_calorie_target, Decimal("2256.00"))
