from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from apps.foods.models import Food
from apps.profiles.models import NutritionalProfile
from apps.tracker.models import Meal, MealItem
from apps.tracker.tasks import send_excess_emails, send_reminder_emails


class NotificationTasksTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="Strong@123",
            is_active=True,
        )
        self.profile = NutritionalProfile.objects.create(
            user=self.user,
            weight_kg=Decimal("80"),
            height_cm=180,
            age=30,
            sex="M",
            activity_level="SEDENTARIO",
            goal="MANUTENCAO",
            daily_calorie_target=Decimal("150.00"),
            remind_interval_hours=3,
        )

    def _create_food(self) -> Food:
        return Food.objects.create(
            name="Food Test",
            kcal_per_100g=Decimal("100.00"),
            protein_per_100g=Decimal("0.00"),
            carbs_per_100g=Decimal("0.00"),
            fat_per_100g=Decimal("0.00"),
            fiber_per_100g=Decimal("0.00"),
            source=Food.FoodSource.MANUAL,
        )

    def test_send_reminder_emails_sends_when_interval_exceeded(self):
        now = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0)

        meal = Meal.objects.create(user=self.user, label=Meal.MealLabel.ALMOCO)
        Meal.objects.filter(pk=meal.pk).update(eaten_at=now - timedelta(hours=4))

        with (
            patch("django.utils.timezone.now", return_value=now),
            patch("django.utils.timezone.localtime", return_value=now),
            patch(
                "apps.accounts.services.ReminderEmailService.send_email"
            ) as send_mock,
        ):
            sent = send_reminder_emails()

        self.assertEqual(sent, 1)
        self.assertTrue(send_mock.called)

    def test_send_reminder_emails_skips_outside_window(self):
        now = timezone.now().replace(hour=23, minute=0, second=0, microsecond=0)
        meal = Meal.objects.create(user=self.user, label=Meal.MealLabel.ALMOCO)
        Meal.objects.filter(pk=meal.pk).update(eaten_at=now - timedelta(hours=4))

        with (
            patch("django.utils.timezone.now", return_value=now),
            patch("django.utils.timezone.localtime", return_value=now),
            patch(
                "apps.accounts.services.ReminderEmailService.send_email"
            ) as send_mock,
        ):
            sent = send_reminder_emails()

        self.assertEqual(sent, 0)
        self.assertFalse(send_mock.called)

    def test_send_excess_emails_sends_when_target_reached(self):
        now = timezone.now().replace(hour=12, minute=0, second=0, microsecond=0)
        food = self._create_food()

        meal = Meal.objects.create(user=self.user, label=Meal.MealLabel.ALMOCO)
        MealItem.objects.create(meal=meal, food=food, quantity_grams=Decimal("200"))

        with (
            patch("django.utils.timezone.now", return_value=now),
            patch("apps.accounts.services.ExcessEmailService.send_email") as send_mock,
        ):
            sent = send_excess_emails()

        self.assertEqual(sent, 1)
        self.assertTrue(send_mock.called)
