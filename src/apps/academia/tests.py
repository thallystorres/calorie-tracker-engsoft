from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.management import call_command
from django.utils import timezone
from apps.academia.models import Exercise, MuscleVolumeGoal, WorkoutSession, WorkoutSet
from apps.academia.repositories import WorkoutRepository
from apps.academia.services import WorkoutTrackerService

# Force-load the management command module so the mock target resolves
from apps.academia.management.commands.seed_exercises import Command as _SeedCommand  # noqa: F401


class WorkoutRepositoryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="repo_user", password="test")
        self.exercise = Exercise.objects.create(name="Supino", muscle_group="chest", description="x")
        self.repo = WorkoutRepository()

    def test_create_event_and_items(self):
        event = self.repo.create_event(user=self.user, name="Treino A")
        items_data = [
            {"exercise": self.exercise, "reps": 10, "weight": 20.0},
        ]
        items = self.repo.create_items(event=event, items_data=items_data)
        self.assertEqual(len(items), 1)
        self.assertEqual(event.sets.count(), 1)
        self.assertEqual(items[0].get_metric(), 200.0)

    def test_get_volume_by_muscle_group(self):
        event = self.repo.create_event(user=self.user, name="Treino A")
        self.repo.create_items(event=event, items_data=[
            {"exercise": self.exercise, "reps": 10, "weight": 20.0},
        ])
        volume = self.repo.get_volume_by_muscle_group(self.user, "chest")
        self.assertEqual(volume, 200.0)


class MuscleVolumeGoalModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.exercise = Exercise.objects.create(
            name="Supino Reto", muscle_group="chest", description="Supino com barra"
        )

    def test_create_muscle_volume_goal(self):
        goal = MuscleVolumeGoal.objects.create(
            user=self.user,
            target_value=5000.0,
            current_value=0.0,
            metric_unit="kg*rep",
            period_start="2025-07-01",
            period_end="2025-07-07",
            muscle_group="chest",
        )
        self.assertEqual(goal.target_value, 5000.0)
        self.assertEqual(goal.metric_unit, "kg*rep")
        self.assertFalse(goal.is_achieved)


class SeedExercisesCommandTests(TestCase):
    @patch("apps.academia.management.commands.seed_exercises.GeminiLLMClient")
    def test_seed_creates_exercises(self, mock_client_class):
        mock_client = mock_client_class.return_value
        mock_client.get_embedding.return_value = [0.0] * 3072
        call_command("seed_exercises")
        self.assertGreater(Exercise.objects.count(), 5)
        exercise = Exercise.objects.first()
        self.assertIsNotNone(exercise.embedding)


class AcademiaPageTemplateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="academia_user", password="test")

    def test_page_renders_for_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get("/academia/")
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("volume-panel", content)
        self.assertIn("history-panel", content)
        self.assertIn("goals-panel", content)
        self.assertIn("workout-form", content)
        self.assertIn("ai-routine-form", content)
        self.assertIn("Registrar Treino", content)
        self.assertIn("Histórico de Treinos", content)
        self.assertIn("Metas de Volume", content)
        self.assertIn("Gerador de Rotina com IA", content)

    def test_page_redirects_for_anonymous_user(self):
        response = self.client.get("/academia/")
        self.assertEqual(response.status_code, 302)


def test_academia_page_view_renders_template():
    from django.test import RequestFactory
    from apps.academia.ui_views import academia_page
    from django.contrib.auth.models import User

    user = User(id=1, username="test")
    rf = RequestFactory()
    req = rf.get("/academia/")
    req.user = user
    resp = academia_page(req)
    assert resp.status_code == 200
    content = resp.content.decode()
    assert "volume-panel" in content
    assert "history-panel" in content
    assert "goals-panel" in content
    assert "workout-form" in content
    assert "ai-routine-form" in content


class WorkoutTrackerServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tracker_user", password="test")
        self.exercise = Exercise.objects.create(name="Supino", muscle_group="chest", description="x")
        self.repo = MagicMock()
        self.service = WorkoutTrackerService(workout_repository=self.repo)

    def test_validate_no_recent_workout_returns_empty_warnings(self):
        items_data = [{"exercise": self.exercise, "reps": 10, "weight": 20.0}]
        warnings = self.service.validate_event_against_profile(self.user, items_data)
        self.assertEqual(warnings, [])

    def test_validate_detects_overtraining(self):
        session = WorkoutSession.objects.create(user=self.user, name="Treino Ontem")
        WorkoutSet.objects.create(session=session, exercise=self.exercise, reps=10, weight=20.0)

        items_data = [{"exercise": self.exercise, "reps": 10, "weight": 20.0}]
        warnings = self.service.validate_event_against_profile(self.user, items_data)
        self.assertEqual(len(warnings), 1)
        self.assertIn("Overtraining", warnings[0])
        self.assertIn("Peitoral", warnings[0])
