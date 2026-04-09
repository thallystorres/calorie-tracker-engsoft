from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.profiles.models import FoodRestriction, NutritionalProfile


class ProfileViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="Forte@1234",
            is_active=True,
        )
        self.url = reverse("profiles:profile")

        self.valid_payload = {
            "weight_kg": "80.00",
            "height_cm": 180,
            "age": 30,
            "sex": "M",
            "activity_level": "SEDENTARIO",
            "goal": "PERDA",
        }

    def test_post_unauthenticated_returns_403(self):
        response = self.client.post(self.url, data=self.valid_payload, format="json")
        self.assertEqual(response.status_code, 403)

    def test_post_creates_new_profile_and_calculates_targets(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=self.valid_payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.user.refresh_from_db()

        profile = self.user.nutritional_profile

        # BMR: (10*80) + (6.25*180) - (5*30) + 5 = 1780
        self.assertEqual(profile.bmr, Decimal("1780.00"))
        # TDEE (Sedentario): 1780 * 1.2 = 2136. Goal (Perda): 2136 - 500 = 1636
        self.assertEqual(profile.daily_calorie_target, Decimal("1636.00"))

    def test_post_returns_400_if_profile_already_exists(self):
        self.client.force_login(self.user)
        NutritionalProfile.objects.create(user=self.user, **self.valid_payload)

        # Tentativa de criar um segundo perfil
        response = self.client.post(self.url, data=self.valid_payload, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["detail"],
            "Perfil nutricional já existe para este usuário. Use PATCH para atualizar.",
        )

    def test_patch_returns_404_if_profile_does_not_exist(self):
        self.client.force_login(self.user)
        response = self.client.patch(
            self.url, data={"weight_kg": "90.00"}, format="json"
        )
        self.assertEqual(response.status_code, 404)

    def test_patch_updates_profile_and_recalculates_targets(self):
        self.client.force_login(self.user)
        profile = NutritionalProfile.objects.create(
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

        # Atualizando peso e objetivo
        patch_payload = {"weight_kg": "90.00", "goal": "MANUTENCAO"}

        response = self.client.patch(self.url, data=patch_payload, format="json")
        self.assertEqual(response.status_code, 200)

        profile.refresh_from_db()
        self.assertEqual(profile.weight_kg, Decimal("90.00"))
        self.assertEqual(profile.goal, "MANUTENCAO")

        # BMR recalculado: (10*90) + (6.25*180) - (5*30) + 5 = 1880
        self.assertEqual(profile.bmr, Decimal("1880.00"))
        # TDEE (Sedentario): 1880 * 1.2 = 2256. Goal (Manutencao) = 2256
        self.assertEqual(profile.daily_calorie_target, Decimal("2256.00"))


class FoodRestrictionViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="Forte@1234",
            is_active=True,
        )
        self.list_create_url = reverse("profiles:restrictions-list-create")

    def test_post_restriction_without_profile_returns_400(self):
        self.client.force_login(self.user)
        payload = {"restriction_type": "VEGANO"}

        response = self.client.post(self.list_create_url, data=payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["detail"],
            "Crie um perfil nutricional primeiro antes de adicionar restrições.",
        )

    def test_post_restriction_with_valid_data_returns_201(self):
        self.client.force_login(self.user)
        NutritionalProfile.objects.create(
            user=self.user,
            weight_kg=80,
            height_cm=180,
            age=30,
            sex="M",
            activity_level="SEDENTARIO",
            goal="PERDA",
        )

        payload = {"restriction_type": "CELIACO"}
        response = self.client.post(self.list_create_url, data=payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(FoodRestriction.objects.count(), 1)
        self.assertEqual(FoodRestriction.objects.first().restriction_type, "CELIACO")

    def test_post_restriction_type_other_requires_description(self):
        self.client.force_login(self.user)
        NutritionalProfile.objects.create(
            user=self.user,
            weight_kg=80,
            height_cm=180,
            age=30,
            sex="M",
            activity_level="SEDENTARIO",
            goal="PERDA",
        )

        payload = {"restriction_type": "OUTRO", "description": ""}
        response = self.client.post(self.list_create_url, data=payload, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("description", response.data)

    def test_delete_restriction_removes_from_database(self):
        self.client.force_login(self.user)
        profile = NutritionalProfile.objects.create(
            user=self.user,
            weight_kg=80,
            height_cm=180,
            age=30,
            sex="M",
            activity_level="SEDENTARIO",
            goal="PERDA",
        )
        restriction = FoodRestriction.objects.create(
            profile=profile, restriction_type="VEGANO"
        )

        detail_url = reverse(
            "profiles:restrictions-detail", kwargs={"pk": restriction.pk}
        )
        response = self.client.delete(detail_url)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(FoodRestriction.objects.count(), 0)

    def test_delete_restriction_from_another_user_returns_404(self):
        self.client.force_login(self.user)
        # Cria perfil para o usuário logado
        NutritionalProfile.objects.create(
            user=self.user,
            weight_kg=80,
            height_cm=180,
            age=30,
            sex="M",
            activity_level="SEDENTARIO",
            goal="PERDA",
        )

        # Cria outro usuário e restrição
        other_user = User.objects.create_user(username="other", password="123")
        other_profile = NutritionalProfile.objects.create(
            user=other_user,
            weight_kg=80,
            height_cm=180,
            age=30,
            sex="M",
            activity_level="SEDENTARIO",
            goal="PERDA",
        )
        restriction = FoodRestriction.objects.create(
            profile=other_profile, restriction_type="VEGANO"
        )

        detail_url = reverse(
            "profiles:restrictions-detail", kwargs={"pk": restriction.pk}
        )
        # Tentando deletar a restrição do outro usuário
        response = self.client.delete(detail_url)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(FoodRestriction.objects.count(), 1)
