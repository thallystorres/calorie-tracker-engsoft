from unittest.mock import MagicMock

from django.contrib.auth.models import AnonymousUser, User
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.signing import BadSignature, SignatureExpired
from django.http import HttpRequest
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.test import APIClient

from .repositories import UserRepository
from .serializers import (
    AccountDeleteSerializer,
    AccountLoginSerializer,
    AccountRegisterSerializer,
    AccountSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
)
from .services import (
    ActivationEmailService,
    ActivationTokenService,
    PasswordResetEmailService,
    PasswordResetTokenService,
    UserService,
)


def create_user(
    *,
    username: str = "user",
    email: str = "user@example.com",
    password: str = "Forte@1234",
    is_active: bool = True,
) -> User:
    return User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name="John",
        last_name="Doe",
        is_active=is_active,
    )


class ActivationTokenServiceTests(TestCase):
    def setUp(self) -> None:
        self.service = ActivationTokenService()
        self.user = User(pk=123, email="foo@example.com")

    def test_generate_contains_user_pk_and_email(self) -> None:
        token = self.service.generate(self.user)
        self.assertIn("123:foo@example.com", token)

    def test_validate_returns_correct_user_id_and_email(self) -> None:
        token = self.service.generate(self.user)
        user_id, email = self.service.validate(token)

        self.assertEqual(user_id, 123)
        self.assertEqual(email, "foo@example.com")

    def test_validate_raises_validation_error_for_expired_token(self) -> None:
        signer = MagicMock()
        signer.unsign.side_effect = SignatureExpired("expired")
        self.service.signer = MagicMock(return_value=signer)

        with self.assertRaises(ValidationError):
            self.service.validate("token")

    def test_validate_raises_validation_error_for_tampered_token(self) -> None:
        signer = MagicMock()
        signer.unsign.side_effect = BadSignature("invalid")
        self.service.signer = MagicMock(return_value=signer)

        with self.assertRaises(ValidationError):
            self.service.validate("token")

    def test_validate_raises_validation_error_for_malformed_payload(self) -> None:
        self.service._unsign = MagicMock(return_value="malformed")

        with self.assertRaises(ValidationError):
            self.service.validate("token")


class PasswordResetTokenServiceTests(TestCase):
    def setUp(self) -> None:
        self.service = PasswordResetTokenService()
        self.user = User(pk=321, email="reset@example.com")

    def test_generate_contains_user_pk_and_email(self) -> None:
        token = self.service.generate(self.user)
        self.assertIn("321:reset@example.com", token)

    def test_validate_returns_correct_user_id_and_email(self) -> None:
        token = self.service.generate(self.user)
        user_id, email = self.service.validate(token)

        self.assertEqual(user_id, 321)
        self.assertEqual(email, "reset@example.com")

    def test_validate_raises_validation_error_for_expired_token(self) -> None:
        signer = MagicMock()
        signer.unsign.side_effect = SignatureExpired("expired")
        self.service.signer = MagicMock(return_value=signer)

        with self.assertRaises(ValidationError):
            self.service.validate("token")

    def test_validate_raises_validation_error_for_tampered_token(self) -> None:
        signer = MagicMock()
        signer.unsign.side_effect = BadSignature("invalid")
        self.service.signer = MagicMock(return_value=signer)

        with self.assertRaises(ValidationError):
            self.service.validate("token")

    def test_validate_raises_validation_error_for_malformed_payload(self) -> None:
        self.service._unsign = MagicMock(return_value="malformed")

        with self.assertRaises(ValidationError):
            self.service.validate("token")


class UserServiceTests(TestCase):
    def setUp(self) -> None:
        self.repo = MagicMock()
        self.activation_token_service = MagicMock()
        self.password_reset_token_service = MagicMock()
        self.activation_email_service = MagicMock()
        self.password_reset_email_service = MagicMock()

        self.service = UserService(
            user_repository=self.repo,
            activation_token_service=self.activation_token_service,
            password_reset_token_service=self.password_reset_token_service,
            activation_email_service=self.activation_email_service,
            password_reset_email_service=self.password_reset_email_service,
        )

    def test_create_account_creates_user_inactive(self) -> None:
        self.repo.create_user.return_value = User(username="new", is_active=False)
        validated_data = {
            "username": "new",
            "email": "new@example.com",
            "first_name": "N",
            "last_name": "U",
            "password": "Forte@1234",
        }

        user = self.service.create_account(validated_data)

        self.assertFalse(user.is_active)
        self.repo.create_user.assert_called_once_with(**validated_data)

    def test_create_account_sends_activation_email(self) -> None:
        user = User(username="new", email="new@example.com", is_active=False)
        self.repo.create_user.return_value = user
        self.service._send_activation_email = MagicMock()

        self.service.create_account(
            {
                "username": "new",
                "email": "new@example.com",
                "first_name": "N",
                "last_name": "U",
                "password": "Forte@1234",
            }
        )

        self.service._send_activation_email.assert_called_once_with(user, None)

    def test_authenticate_account_returns_user_for_valid_credentials(self) -> None:
        user = create_user(username="valid", password="Forte@1234", is_active=True)
        self.repo.get_by_username_or_email.return_value = user

        authenticated = self.service.authenticate_account(
            username_or_email="valid", password="Forte@1234"
        )

        self.assertEqual(authenticated.id, user.id)

    def test_authenticate_account_raises_for_wrong_password(self) -> None:
        user = create_user(username="valid", password="Forte@1234", is_active=True)
        self.repo.get_by_username_or_email.return_value = user

        with self.assertRaises(AuthenticationFailed):
            self.service.authenticate_account(
                username_or_email="valid", password="Errada@123"
            )

    def test_authenticate_account_raises_for_missing_user(self) -> None:
        self.repo.get_by_username_or_email.return_value = None

        with self.assertRaises(AuthenticationFailed):
            self.service.authenticate_account(
                username_or_email="missing", password="Errada@123"
            )

    def test_authenticate_account_raises_for_inactive_user(self) -> None:
        user = create_user(username="inactive", password="Forte@1234", is_active=False)
        self.repo.get_by_username_or_email.return_value = user

        with self.assertRaises(AuthenticationFailed):
            self.service.authenticate_account(
                username_or_email="inactive", password="Forte@1234"
            )

    def test_activate_account_activates_user_with_valid_token(self) -> None:
        user = create_user(username="inactive2", email="u@example.com", is_active=False)
        self.activation_token_service.validate.return_value = (user.id, user.email)
        self.repo.get_by_user_id.return_value = user

        activated = self.service.activate_account("valid-token")

        self.assertEqual(activated.id, user.id)
        self.repo.activate.assert_called_once_with(user)

    def test_activate_account_raises_validation_error_for_missing_user(self) -> None:
        self.activation_token_service.validate.return_value = (9999, "u@example.com")
        self.repo.get_by_user_id.return_value = None

        with self.assertRaises(ValidationError):
            self.service.activate_account("valid-token")

    def test_activate_account_raises_validation_error_for_mismatched_email(
        self,
    ) -> None:
        user = create_user(email="real@example.com")
        self.activation_token_service.validate.return_value = (
            user.id,
            "fake@example.com",
        )
        self.repo.get_by_user_id.return_value = user

        with self.assertRaises(ValidationError):
            self.service.activate_account("valid-token")

    def test_update_account_updates_fields(self) -> None:
        user = create_user(email="old@example.com")
        updated = User(
            id=user.id,
            username=user.username,
            email="old@example.com",
            first_name="Novo",
            last_name="Sobrenome",
            is_active=user.is_active,
        )
        self.repo.update_user.return_value = updated

        returned_user, _ = self.service.update_account(
            user=user,
            validated_data={"first_name": "Novo", "last_name": "Sobrenome"},
        )

        self.assertEqual(returned_user.first_name, "Novo")
        self.assertEqual(returned_user.last_name, "Sobrenome")

    def test_update_account_without_email_change_returns_false(self) -> None:
        user = create_user(email="same@example.com")
        updated = User(
            id=user.id,
            username=user.username,
            email="same@example.com",
            first_name="Novo",
            is_active=user.is_active,
        )
        self.repo.update_user.return_value = updated

        _, email_changed = self.service.update_account(
            user=user,
            validated_data={"first_name": "Novo"},
        )

        self.assertFalse(email_changed)
        self.repo.deactivate.assert_not_called()

    def test_update_account_with_email_change_deactivates_and_sends_email(self) -> None:
        user = create_user(email="old@example.com")
        updated = User(
            id=user.id,
            username=user.username,
            email="new@example.com",
            is_active=True,
        )
        self.repo.update_user.return_value = updated
        self.service._send_activation_email = MagicMock()

        _, email_changed = self.service.update_account(
            user=user,
            validated_data={"email": "new@example.com"},
            request=HttpRequest(),
        )

        self.assertTrue(email_changed)
        self.repo.deactivate.assert_called_once_with(updated)
        self.service._send_activation_email.assert_called_once()

    def test_delete_account_deactivates_active_account(self) -> None:
        user = create_user(is_active=True)

        self.service.delete_account(user=user)

        self.repo.deactivate.assert_called_once_with(user)

    def test_delete_account_does_not_change_inactive_account(self) -> None:
        user = create_user(
            username="inactive3", email="inactive3@example.com", is_active=False
        )

        self.service.delete_account(user=user)

        self.repo.deactivate.assert_not_called()

    def test_request_password_reset_does_not_send_for_missing_user(self) -> None:
        self.repo.get_by_email.return_value = None
        self.service._send_token_email = MagicMock()

        self.service.request_password_reset(email="missing@example.com")

        self.service._send_token_email.assert_not_called()

    def test_request_password_reset_does_not_send_for_inactive_user(self) -> None:
        user = create_user(username="u2", email="u2@example.com", is_active=False)
        self.repo.get_by_email.return_value = user
        self.service._send_token_email = MagicMock()

        self.service.request_password_reset(email="u2@example.com")

        self.service._send_token_email.assert_not_called()

    def test_request_password_reset_sends_for_active_user(self) -> None:
        user = create_user(username="u3", email="u3@example.com", is_active=True)
        self.repo.get_by_email.return_value = user
        self.service._send_token_email = MagicMock()

        self.service.request_password_reset(email="u3@example.com")

        self.service._send_token_email.assert_called_once()

    def test_reset_password_with_token_updates_password(self) -> None:
        user = create_user(username="u4", email="u4@example.com", is_active=True)
        self.password_reset_token_service.validate.return_value = (user.id, user.email)
        self.repo.get_by_user_id.return_value = user

        self.service.reset_password_with_token(token="valid", new_password="Nova@12345")

        self.repo.update_password.assert_called_once_with(
            user=user,
            new_password="Nova@12345",
        )

    def test_reset_password_with_token_raises_for_invalid_password(self) -> None:
        user = create_user(username="u5", email="u5@example.com", is_active=True)
        self.password_reset_token_service.validate.return_value = (user.id, user.email)
        self.repo.get_by_user_id.return_value = user

        with self.assertRaises(ValidationError):
            self.service.reset_password_with_token(token="valid", new_password="123")

    def test_reset_password_with_token_raises_for_missing_user(self) -> None:
        self.password_reset_token_service.validate.return_value = (
            9000,
            "u6@example.com",
        )
        self.repo.get_by_user_id.return_value = None

        with self.assertRaises(ValidationError):
            self.service.reset_password_with_token(
                token="valid", new_password="Nova@12345"
            )

    def test_reset_password_with_token_raises_for_mismatched_email(self) -> None:
        user = create_user(username="u7", email="real@example.com", is_active=True)
        self.password_reset_token_service.validate.return_value = (
            user.id,
            "fake@example.com",
        )
        self.repo.get_by_user_id.return_value = user

        with self.assertRaises(ValidationError):
            self.service.reset_password_with_token(
                token="valid", new_password="Nova@12345"
            )


class ActivationEmailServiceTests(TestCase):
    def setUp(self) -> None:
        self.service = ActivationEmailService()
        self.factory = RequestFactory()
        self.user = User(username="mailuser", email="mail@example.com")

    def test_build_url_with_token(self) -> None:
        request = self.factory.get("/")
        url = self.service.build_url(token="abc", request=request)

        self.assertIn("/accounts/verify-email/abc/", url)

    def test_build_url_without_request_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            self.service.build_url(token="abc", request=None)

    def test_send_email_calls_send_mail_with_correct_recipient(self) -> None:
        self.service._send_text_email = MagicMock()
        request = self.factory.get("/")

        self.service.send_email(user=self.user, token="abc", request=request)

        self.service._send_text_email.assert_called_once()
        kwargs = self.service._send_text_email.call_args.kwargs
        self.assertEqual(kwargs["recipient"], "mail@example.com")


class PasswordResetEmailServiceTests(TestCase):
    def setUp(self) -> None:
        self.service = PasswordResetEmailService()
        self.factory = RequestFactory()
        self.user = User(username="mailuser2", email="mail2@example.com")

    def test_build_url_with_token(self) -> None:
        request = self.factory.get("/")
        url = self.service.build_url(token="abc", request=request)

        self.assertIn("/accounts/password-reset/confirm/abc/", url)

    def test_build_url_without_request_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            self.service.build_url(token="abc", request=None)

    def test_send_email_calls_send_mail_with_correct_recipient(self) -> None:
        self.service._send_text_email = MagicMock()
        request = self.factory.get("/")

        self.service.send_email(user=self.user, token="abc", request=request)

        self.service._send_text_email.assert_called_once()
        kwargs = self.service._send_text_email.call_args.kwargs
        self.assertEqual(kwargs["recipient"], "mail2@example.com")


class UserRepositoryTests(TestCase):
    def setUp(self) -> None:
        self.repo = UserRepository()

    def test_create_user_persists_with_hashed_password(self) -> None:
        user = self.repo.create_user(
            username="repo_user",
            email="repo@example.com",
            first_name="Repo",
            last_name="User",
            password="Forte@1234",
        )

        self.assertTrue(user.check_password("Forte@1234"))
        self.assertFalse(user.is_active)

    def test_exists_by_username_returns_true_for_existing_user(self) -> None:
        create_user(username="exists_username", email="a1@example.com")
        self.assertTrue(self.repo.exists_by_username("exists_username"))

    def test_exists_by_email_returns_true_ignoring_case(self) -> None:
        create_user(username="exists_email", email="exists@example.com")
        self.assertTrue(self.repo.exists_by_email("EXISTS@example.com"))

    def test_exists_by_email_ignores_current_user_when_user_id_provided(self) -> None:
        user = create_user(username="same_user", email="same@example.com")
        self.assertFalse(self.repo.exists_by_email("same@example.com", user.id))

    def test_get_by_username_returns_correct_user(self) -> None:
        user = create_user(username="by_username", email="by_username@example.com")
        found = self.repo.get_by_username("by_username")
        self.assertEqual(found.id, user.id)

    def test_get_by_email_returns_correct_user_ignoring_case(self) -> None:
        user = create_user(username="by_email", email="by_email@example.com")
        found = self.repo.get_by_email("BY_EMAIL@example.com")
        self.assertEqual(found.id, user.id)

    def test_get_by_username_or_email_finds_by_username(self) -> None:
        user = create_user(username="find_u", email="find_u@example.com")
        found = self.repo.get_by_username_or_email("find_u")
        self.assertEqual(found.id, user.id)

    def test_get_by_username_or_email_finds_by_email(self) -> None:
        user = create_user(username="find_e", email="find_e@example.com")
        found = self.repo.get_by_username_or_email("find_e@example.com")
        self.assertEqual(found.id, user.id)

    def test_get_by_username_or_email_returns_none_for_missing(self) -> None:
        self.assertIsNone(self.repo.get_by_username_or_email("missing"))

    def test_get_by_user_id_returns_correct_user(self) -> None:
        user = create_user(username="by_id", email="by_id@example.com")
        found = self.repo.get_by_user_id(user.id)
        self.assertEqual(found.id, user.id)

    def test_get_by_user_id_returns_none_for_missing_id(self) -> None:
        self.assertIsNone(self.repo.get_by_user_id(987654))

    def test_activate_sets_user_active(self) -> None:
        user = create_user(
            username="inactive_repo", email="inactive_repo@example.com", is_active=False
        )
        self.repo.activate(user)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_deactivate_sets_user_inactive(self) -> None:
        user = create_user(
            username="active_repo", email="active_repo@example.com", is_active=True
        )
        self.repo.deactivate(user)
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    def test_update_user_updates_only_supported_fields(self) -> None:
        user = create_user(
            username="upd_repo",
            email="upd_repo@example.com",
            is_active=True,
        )
        old_username = user.username

        self.repo.update_user(
            user=user,
            data={
                "email": "updated@example.com",
                "first_name": "Nome",
                "last_name": "Sobrenome",
                "username": "should_not_change",
            },
        )
        user.refresh_from_db()

        self.assertEqual(user.email, "updated@example.com")
        self.assertEqual(user.first_name, "Nome")
        self.assertEqual(user.last_name, "Sobrenome")
        self.assertEqual(user.username, old_username)

    def test_update_password_updates_hashed_password(self) -> None:
        user = create_user(
            username="upd_pwd",
            email="upd_pwd@example.com",
            password="Velha@12345",
        )

        self.repo.update_password(user=user, new_password="Nova@12345")
        user.refresh_from_db()

        self.assertTrue(user.check_password("Nova@12345"))


class SerializerTests(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_account_register_serializer_normalizes_email(self) -> None:
        serializer = AccountRegisterSerializer(
            data={
                "username": "new_user_1",
                "email": "  User@Example.COM  ",
                "first_name": "New",
                "last_name": "User",
                "password": "Forte@1234",
                "confirm_password": "Forte@1234",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["email"], "user@example.com")

    def test_account_register_serializer_rejects_duplicate_username(self) -> None:
        create_user(username="dup_user", email="dup1@example.com")

        serializer = AccountRegisterSerializer(
            data={
                "username": "dup_user",
                "email": "new@example.com",
                "first_name": "X",
                "last_name": "Y",
                "password": "Forte@1234",
                "confirm_password": "Forte@1234",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)

    def test_account_register_serializer_rejects_duplicate_email(self) -> None:
        create_user(username="dup_email_user", email="dup_email@example.com")

        serializer = AccountRegisterSerializer(
            data={
                "username": "other_user",
                "email": "DUP_EMAIL@example.com",
                "first_name": "X",
                "last_name": "Y",
                "password": "Forte@1234",
                "confirm_password": "Forte@1234",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_account_register_serializer_rejects_mismatched_confirm_password(
        self,
    ) -> None:
        serializer = AccountRegisterSerializer(
            data={
                "username": "new_user_2",
                "email": "new2@example.com",
                "first_name": "X",
                "last_name": "Y",
                "password": "Forte@1234",
                "confirm_password": "Outro@1234",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("confirm_password", serializer.errors)

    def test_account_register_serializer_rejects_weak_password(self) -> None:
        serializer = AccountRegisterSerializer(
            data={
                "username": "new_user_3",
                "email": "new3@example.com",
                "first_name": "X",
                "last_name": "Y",
                "password": "123",
                "confirm_password": "123",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_account_serializer_does_not_allow_username_change(self) -> None:
        user = create_user(username="immutable_username", email="immutable@example.com")
        serializer = AccountSerializer(
            user,
            data={"username": "new_name", "first_name": "Updated"},
            partial=True,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn("username", serializer.validated_data)

    def test_account_serializer_rejects_email_used_by_other_user(self) -> None:
        owner = create_user(username="owner", email="owner@example.com")
        create_user(username="other", email="other@example.com")

        serializer = AccountSerializer(
            owner,
            data={"email": "OTHER@example.com"},
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_account_login_serializer_validates_and_injects_user(self) -> None:
        user = create_user(username="login_ser", email="login_ser@example.com")
        mocked_service = MagicMock()
        mocked_service.authenticate_account.return_value = user

        serializer = AccountLoginSerializer(
            data={"username_or_email": " login_ser ", "password": "Forte@1234"},
            user_service=mocked_service,
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["user"].id, user.id)

    def test_account_delete_serializer_rejects_unauthenticated_user(self) -> None:
        request = self.factory.post("/api/accounts/me/")
        request.user = AnonymousUser()

        serializer = AccountDeleteSerializer(
            data={"password": "any"}, context={"request": request}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_account_delete_serializer_rejects_incorrect_password(self) -> None:
        user = create_user(
            username="del_ser", email="del_ser@example.com", password="Certa@1234"
        )
        request = self.factory.post("/api/accounts/me/")
        request.user = user

        serializer = AccountDeleteSerializer(
            data={"password": "Errada@1234"}, context={"request": request}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_password_reset_request_serializer_normalizes_email(self) -> None:
        serializer = PasswordResetRequestSerializer(
            data={"email": "  Mail@Example.Com  "}
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["email"], "mail@example.com")

    def test_password_reset_confirm_serializer_rejects_mismatched_confirm_password(
        self,
    ) -> None:
        serializer = PasswordResetConfirmSerializer(
            data={
                "new_password": "Nova@12345",
                "confirm_password": "Outra@12345",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("confirm_password", serializer.errors)

    def test_password_reset_confirm_serializer_rejects_weak_password(self) -> None:
        serializer = PasswordResetConfirmSerializer(
            data={
                "new_password": "123",
                "confirm_password": "123",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)


class EndpointsIntegrationTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_register_returns_201_with_valid_data(self) -> None:
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "register_ok",
                "email": "register_ok@example.com",
                "first_name": "Reg",
                "last_name": "Ok",
                "password": "Forte@1234",
                "confirm_password": "Forte@1234",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

    def test_register_returns_400_for_duplicate_username_or_email(self) -> None:
        create_user(username="dup_reg", email="dup_reg@example.com")

        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "dup_reg",
                "email": "dup_reg@example.com",
                "first_name": "Reg",
                "last_name": "Dup",
                "password": "Forte@1234",
                "confirm_password": "Forte@1234",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_register_returns_400_for_weak_password(self) -> None:
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "register_weak",
                "email": "register_weak@example.com",
                "first_name": "Reg",
                "last_name": "Weak",
                "password": "123",
                "confirm_password": "123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_register_returns_403_for_authenticated_user(self) -> None:
        user = create_user(username="auth_reg", email="auth_reg@example.com")
        self.client.force_authenticate(user=user)

        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "register_auth",
                "email": "register_auth@example.com",
                "first_name": "Reg",
                "last_name": "Auth",
                "password": "Forte@1234",
                "confirm_password": "Forte@1234",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_login_returns_200_and_creates_session_for_valid_credentials(self) -> None:
        create_user(
            username="login_ok", email="login_ok@example.com", password="Forte@1234"
        )

        response = self.client.post(
            reverse("accounts:login"),
            {"username_or_email": "login_ok", "password": "Forte@1234"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_returns_400_for_invalid_payload(self) -> None:
        response = self.client.post(
            reverse("accounts:login"),
            {"username_or_email": "login_ok"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_login_returns_403_for_invalid_credentials_or_inactive_account(
        self,
    ) -> None:
        create_user(
            username="login_fail", email="login_fail@example.com", password="Forte@1234"
        )
        create_user(
            username="login_inactive",
            email="login_inactive@example.com",
            password="Forte@1234",
            is_active=False,
        )

        wrong_password = self.client.post(
            reverse("accounts:login"),
            {"username_or_email": "login_fail", "password": "Errada@1234"},
            format="json",
        )
        missing_user = self.client.post(
            reverse("accounts:login"),
            {"username_or_email": "does-not-exist", "password": "Errada@1234"},
            format="json",
        )
        inactive = self.client.post(
            reverse("accounts:login"),
            {"username_or_email": "login_inactive", "password": "Forte@1234"},
            format="json",
        )

        self.assertEqual(wrong_password.status_code, 403)
        self.assertEqual(missing_user.status_code, 403)
        self.assertEqual(inactive.status_code, 403)

    def test_logout_returns_200_and_destroys_session(self) -> None:
        user = create_user(username="logout_ok", email="logout_ok@example.com")
        self.client.force_login(user)

        response = self.client.post(reverse("accounts:logout"), {}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_returns_403_for_unauthenticated_user(self) -> None:
        response = self.client.post(reverse("accounts:logout"), {}, format="json")
        self.assertEqual(response.status_code, 403)

    def test_activate_returns_200_for_valid_token(self) -> None:
        user = create_user(
            username="activate_ok", email="activate_ok@example.com", is_active=False
        )
        token = ActivationTokenService().generate(user)

        response = self.client.get(reverse("accounts:activate"), {"token": token})

        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    @override_settings(ACCOUNT_ACTIVATION_MAX_AGE_SECONDS=0)
    def test_activate_returns_400_for_expired_invalid_or_mismatched_token(self) -> None:
        user = create_user(
            username="activate_bad", email="activate_bad@example.com", is_active=False
        )
        valid_token = ActivationTokenService().generate(user)

        user.email = "changed@example.com"
        user.save(update_fields=["email"])

        mismatched = self.client.get(
            reverse("accounts:activate"), {"token": valid_token}
        )
        malformed = self.client.get(
            reverse("accounts:activate"), {"token": "malformed"}
        )

        self.assertEqual(mismatched.status_code, 400)
        self.assertEqual(malformed.status_code, 400)

    def test_activate_without_token_returns_400(self) -> None:
        response = self.client.get(reverse("accounts:activate"))
        self.assertEqual(response.status_code, 400)

    def test_me_get_returns_200_for_authenticated_user(self) -> None:
        user = create_user(username="me_get", email="me_get@example.com")
        self.client.force_login(user)

        response = self.client.get(reverse("accounts:me"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "me_get")

    def test_me_get_returns_403_for_unauthenticated_user(self) -> None:
        response = self.client.get(reverse("accounts:me"))
        self.assertEqual(response.status_code, 403)

    def test_me_patch_returns_200_without_email_change(self) -> None:
        user = create_user(username="me_patch_1", email="me_patch_1@example.com")
        self.client.force_login(user)

        response = self.client.patch(
            reverse("accounts:me"),
            {"first_name": "Novo"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertEqual(user.first_name, "Novo")
        self.assertTrue(user.is_active)
        self.assertIn("_auth_user_id", self.client.session)

    def test_me_patch_returns_200_with_email_change_and_logs_out(self) -> None:
        user = create_user(username="me_patch_2", email="me_patch_2@example.com")
        self.client.force_login(user)

        response = self.client.patch(
            reverse("accounts:me"),
            {"email": "new_me_patch_2@example.com"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertEqual(user.email, "new_me_patch_2@example.com")
        self.assertFalse(user.is_active)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_me_patch_returns_400_for_duplicate_email(self) -> None:
        user = create_user(username="me_patch_3", email="me_patch_3@example.com")
        create_user(username="someone_else", email="someone_else@example.com")
        self.client.force_login(user)

        response = self.client.patch(
            reverse("accounts:me"),
            {"email": "someone_else@example.com"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_me_patch_returns_403_for_unauthenticated_user(self) -> None:
        response = self.client.patch(
            reverse("accounts:me"),
            {"first_name": "Novo"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_me_delete_returns_204_with_correct_password(self) -> None:
        user = create_user(
            username="me_del_ok",
            email="me_del_ok@example.com",
            password="Certa@1234",
            is_active=True,
        )
        self.client.force_login(user)

        response = self.client.delete(
            reverse("accounts:me"),
            {"password": "Certa@1234"},
            format="json",
        )

        self.assertEqual(response.status_code, 204)
        user.refresh_from_db()
        self.assertFalse(user.is_active)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_me_delete_returns_400_for_wrong_password(self) -> None:
        user = create_user(
            username="me_del_bad",
            email="me_del_bad@example.com",
            password="Certa@1234",
            is_active=True,
        )
        self.client.force_login(user)

        response = self.client.delete(
            reverse("accounts:me"),
            {"password": "Errada@1234"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_me_delete_returns_403_for_unauthenticated_user(self) -> None:
        response = self.client.delete(
            reverse("accounts:me"),
            {"password": "Certa@1234"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_password_reset_request_returns_200_for_existing_and_missing_email(
        self,
    ) -> None:
        create_user(username="reset_req", email="reset_req@example.com", is_active=True)

        existing = self.client.post(
            reverse("accounts:password-reset-request"),
            {"email": "reset_req@example.com"},
            format="json",
        )
        missing = self.client.post(
            reverse("accounts:password-reset-request"),
            {"email": "missing_reset_req@example.com"},
            format="json",
        )

        self.assertEqual(existing.status_code, 200)
        self.assertEqual(missing.status_code, 200)

    def test_password_reset_confirm_returns_200_for_valid_token_and_strong_password(
        self,
    ) -> None:
        user = create_user(
            username="reset_confirm_ok",
            email="reset_confirm_ok@example.com",
            password="Antiga@1234",
            is_active=True,
        )
        token = PasswordResetTokenService().generate(user)

        response = self.client.post(
            reverse("accounts:password-reset-confirm"),
            {
                "new_password": "NovaSenha@1234",
                "confirm_password": "NovaSenha@1234",
            },
            format="json",
            QUERY_STRING=f"token={token}",
        )

        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.check_password("NovaSenha@1234"))

    def test_password_reset_confirm_returns_400_for_invalid_or_malformed_token(
        self,
    ) -> None:
        response = self.client.post(
            reverse("accounts:password-reset-confirm"),
            {
                "new_password": "NovaSenha@1234",
                "confirm_password": "NovaSenha@1234",
            },
            format="json",
            QUERY_STRING="token=malformed",
        )

        self.assertEqual(response.status_code, 400)

    def test_password_reset_confirm_without_token_returns_400(self) -> None:
        response = self.client.post(
            reverse("accounts:password-reset-confirm"),
            {
                "new_password": "NovaSenha@1234",
                "confirm_password": "NovaSenha@1234",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_password_reset_confirm_returns_400_for_weak_password(self) -> None:
        user = create_user(
            username="reset_confirm_weak",
            email="reset_confirm_weak@example.com",
            password="Antiga@1234",
            is_active=True,
        )
        token = PasswordResetTokenService().generate(user)

        response = self.client.post(
            reverse("accounts:password-reset-confirm"),
            {
                "new_password": "123",
                "confirm_password": "123",
            },
            format="json",
            QUERY_STRING=f"token={token}",
        )

        self.assertEqual(response.status_code, 400)
