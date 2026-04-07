import logging
from abc import ABC, abstractmethod
from typing import Any
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.urls import reverse
from rest_framework.exceptions import AuthenticationFailed, ValidationError

from .repositories import UserRepository

logging.basicConfig(
    filename="kraken_sitac.log",
    format="%(asctime)s - %(message)s",
    datefmt="%d/%m/%Y %I:%M:%S %p",
    encoding="utf-8",
    level=logging.INFO,
)


class BaseSignedTokenService:
    signer_salt_setting: str
    max_age_setting: str
    signature_expired_msg: str
    bad_signature_msg: str
    malformed_msg: str

    def signer(self) -> TimestampSigner:
        return TimestampSigner(salt=getattr(settings, self.signer_salt_setting))

    def generate(self, user: User) -> str:
        payload = f"{user.pk}:{user.email}"
        return self.signer().sign(payload)

    def _unsign(self, token: str) -> str:
        try:
            return self.signer().unsign(
                token, max_age=getattr(settings, self.max_age_setting)
            )

        except SignatureExpired as e:
            raise ValidationError(self.signature_expired_msg) from e

        except BadSignature as e:
            raise ValidationError(self.bad_signature_msg) from e

    def _extract_payload(self, unsigned: str) -> tuple[int, str]:
        try:
            user_id_str, email = unsigned.split(":", 1)
            return int(user_id_str), email
        except (TypeError, ValueError) as e:
            raise ValidationError(self.malformed_msg) from e

    def validate(self, token: str) -> tuple[int, str]:
        unsigned = self._unsign(token)
        return self._extract_payload(unsigned)


class ActivationTokenService(BaseSignedTokenService):
    signer_salt_setting = "ACCOUNT_ACTIVATION_SALT"
    max_age_setting = "ACCOUNT_ACTIVATION_MAX_AGE_SECONDS"
    signature_expired_msg = "Link de ativação expirado."
    bad_signature_msg = "Link de ativação inválido."
    malformed_msg = "Token de ativação malformado."


class PasswordResetTokenService(BaseSignedTokenService):
    signer_salt_setting = "PASSWORD_RESET_SALT"
    max_age_setting = "PASSWORD_RESET_MAX_AGE_SECONDS"
    signature_expired_msg = "Token de redefinição expirado."
    bad_signature_msg = "Token de redefinição inválido."
    malformed_msg = "Token de redefinição malformado."


class BaseEmailService(ABC):
    route_name: str
    missing_request_msg: str
    subject: str

    def _build_url_with_token(self, token: str, request=None) -> str:
        path = reverse(self.route_name)
        query = urlencode({"token": token})

        if request is None:
            raise ValidationError(self.missing_request_msg)
        return request.build_absolute_uri(f"{path}?{query}")

    def build_url(self, *, token: str, request=None) -> str:
        return self._build_url_with_token(token=token, request=request)

    def _send_text_email(self, *, recipient: str, message: str) -> None:
        send_mail(
            subject=self.subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )

    @abstractmethod
    def build_message(self, *, user: User, url: str) -> str:
        raise NotImplementedError

    def send_email(self, *, user: User, token: str, request=None) -> None:
        url = self.build_url(
            token=token,
            request=request,
        )
        message = self.build_message(user=user, url=url)
        self._send_text_email(recipient=user.email, message=message)


class ActivationEmailService(BaseEmailService):
    route_name = "accounts:activate"
    missing_request_msg = "Não foi possível montar URL de ativação sem request"
    subject = "Ative sua conta"

    def build_message(self, *, user: User, url: str) -> str:
        return (
            f"Olá, {user.first_name or user.username}!\n\n"
            "Seu cadastro foi realizado com sucesso.\n"
            "Para ativar sua conta acesse o link abaixo:\n\n"
            f"{url}\n\n"
            "Se você não solicitou esse cadastro ignore esse e-mail."
        )


class PasswordResetEmailService(BaseEmailService):
    route_name = "accounts:password-reset-confirm"
    missing_request_msg = "Não foi possível montar URL de redefinição sem request"
    subject = "Redefinição de senha"

    def build_message(self, *, user: User, url: str) -> str:
        return (
            f"Olá, {user.first_name or user.username}!\n\n"
            "Recebemos uma solicitação para redefinir sua senha.\n"
            "Acesse o link abaixo para continuar\n\n"
            f"{url}\n\n"
            "Se você não solicitou esse cadastro ignore esse e-mail."
        )


class UserService:
    def __init__(
        self,
        *,
        user_repository: UserRepository,
        activation_token_service: BaseSignedTokenService,
        password_reset_token_service: BaseSignedTokenService,
        activation_email_service: BaseEmailService,
        password_reset_email_service: BaseEmailService,
    ) -> None:
        self._repo = user_repository
        self._activation_token = activation_token_service
        self._reset_token = password_reset_token_service
        self._activation_email = activation_email_service
        self._reset_email = password_reset_email_service

    def create_account(self, validated_data: dict[str, Any], request=None) -> User:
        user = self._repo.create_user(**validated_data)
        self._send_activation_email(user, request)
        return user

    def update_account(
        self, *, user: User, validated_data: dict[str, Any], request=None
    ) -> tuple[User, bool]:
        old_email = self._normalize_email(user.email)
        user = self._repo.update_user(user=user, data=validated_data)

        email_changed = old_email != self._normalize_email(user.email)
        if email_changed:
            self._repo.deactivate(user)
            self._send_activation_email(user, request)

        return user, email_changed

    def authenticate_account(self, *, username_or_email: str, password: str) -> User:
        user = self._repo.get_by_username_or_email(username_or_email)

        if user is None or not user.check_password(password) or not user.is_active:
            raise AuthenticationFailed("Credenciais inválidas.")

        return user

    def activate_account(self, token: str) -> User:
        user = self._get_user_from_token(
            token=token,
            token_service=self._activation_token,
            not_found_msg="Usuário do link de ativação não encontrado",
            invalid_user_msg="Link de ativação inválido para este usuário",
        )

        if not user.is_active:
            self._repo.activate(user)

        return user

    def delete_account(self, *, user: User) -> None:
        if not user.is_active:
            return
        self._repo.deactivate(user)
        logging.info("Conta desativada via soft delete. user_pk=%s", user.pk)

    def request_password_reset(self, *, email: str, request=None) -> None:
        user = self._repo.get_by_email(self._normalize_email(email))

        if user is None or not user.is_active:
            return

        self._send_token_email(
            user=user,
            token_service=self._reset_token,
            email_service=self._reset_email,
            request=request,
            log_msg="Falha ao enviar e-mail de redefinicao de senha para user_pk=%s",
        )

    def reset_password_with_token(self, *, token: str, new_password: str) -> User:
        user = self._get_user_from_token(
            token=token,
            token_service=self._reset_token,
            not_found_msg="Usuário do link de redefinição não encontrado.",
            invalid_user_msg="Link de redefinição inválido para este usuário.",
        )

        try:
            validate_password(password=new_password, user=user)
        except DjangoValidationError as e:
            raise ValidationError({"new_password": e.messages}) from e

        self._repo.update_password(user=user, new_password=new_password)
        return user

    def _send_activation_email(self, user: User, request=None) -> None:
        self._send_token_email(
            user=user,
            token_service=self._activation_token,
            email_service=self._activation_email,
            request=request,
            log_msg="Falha ao enviar e-mail de ativacao para user_pk=%s",
        )

    def _send_token_email(
        self,
        *,
        user: User,
        token_service: BaseSignedTokenService,
        email_service: BaseEmailService,
        log_msg: str,
        request=None,
    ) -> None:
        try:
            token = token_service.generate(user)
            email_service.send_email(user=user, token=token, request=request)
        except Exception:
            logging.exception(log_msg, user.pk)

    def _get_user_from_token(
        self,
        *,
        token: str,
        token_service: BaseSignedTokenService,
        not_found_msg: str,
        invalid_user_msg: str,
    ) -> User:
        user_id, email = token_service.validate(token)
        user = self._repo.get_by_user_id(user_id)

        if user is None:
            raise ValidationError(not_found_msg)

        if self._normalize_email(user.email) != self._normalize_email(email):
            raise ValidationError(invalid_user_msg)

        return user

    @staticmethod
    def _normalize_email(email: str | None) -> str:
        return (email or "").strip().lower()
