import logging
from datetime import timedelta

from celery import shared_task
from django.contrib.auth.models import User
from django.utils import timezone

from apps.accounts.services import ExcessEmailService, ReminderEmailService
from apps.tracker.models import Meal
from apps.tracker.repositories import MealRepository

logger = logging.getLogger(__name__)


def _is_within_reminder_window(now_local) -> bool:
    return 8 <= now_local.hour < 22


@shared_task
def send_reminder_emails() -> int:
    now = timezone.now()
    now_local = timezone.localtime(now)
    if not _is_within_reminder_window(now_local):
        return 0

    today = now_local.date()
    users = (
        User.objects.filter(is_active=True, nutritional_profile__isnull=False)
        .select_related("nutritional_profile")
        .iterator()
    )

    email_service = ReminderEmailService()
    sent = 0

    for user in users:
        last_meal = (
            Meal.objects.filter(user=user, eaten_at__date=today)
            .order_by("-eaten_at")
            .first()
        )
        if last_meal is None:
            continue

        interval_hours = user.nutritional_profile.remind_interval_hours or 3
        delta = now - last_meal.eaten_at
        if delta >= timedelta(hours=interval_hours):
            email_service.send_email(user=user)
            logger.info(
                "REMINDER_EMAIL_SENT user_pk=%s recipient=%s", user.pk, user.email
            )
            sent += 1

    return sent


@shared_task
def send_excess_emails() -> int:
    now_local = timezone.localtime(timezone.now())
    today = now_local.date()

    users = (
        User.objects.filter(is_active=True, nutritional_profile__isnull=False)
        .select_related("nutritional_profile")
        .iterator()
    )

    meal_repo = MealRepository()
    email_service = ExcessEmailService()
    sent = 0

    for user in users:
        profile = user.nutritional_profile
        if profile.daily_calorie_target is None:
            continue

        totals = meal_repo.get_daily_totals(user, today)
        total_kcal = totals.get("kcal") or 0
        if total_kcal >= profile.daily_calorie_target:
            email_service.send_email(user=user)
            logger.info(
                "EXCESS_EMAIL_SENT user_pk=%s recipient=%s", user.pk, user.email
            )
            sent += 1

    return sent
