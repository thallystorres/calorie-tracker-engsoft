import logging
from typing import Any
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.models import User
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


class UserService:
    @staticmethod
    def create_account(validated_data: dict[str, Any], request=None) -> User:
        user = UserRepository.create_user(**validated_data)
        UserService.send_email_activation(user, request)
        return user

    @staticmethod
    def update_account(
        *, user: User, validated_data: dict[str, Any], request=None
    ) -> tuple[User, bool]:
        old_email = (user.email or "").strip().lower()
        user = UserRepository.update_user(user=user, data=validated_data)

        email_changed = UserService._email_changed(user=user, old_email=old_email)
        if email_changed:
            UserService._handle_email_change(user=user, request=request)

        return user, email_changed

    @staticmethod
    def authenticate_account(*, username_or_email: str, password: str):
        invalid_credentials_msg = "Credenciais inválidas."
        user = UserRepository.get_by_username_or_email(username_or_email)

        if user is None or not user.check_password(password) or not user.is_active:
            raise AuthenticationFailed(invalid_credentials_msg)

        return user

    @staticmethod
    def _email_changed(*, user: User, old_email: str) -> bool:
        new_email = (user.email or "").strip().lower()
        return old_email != new_email

    @staticmethod
    def _handle_email_change(*, user: User, request=None) -> None:
        UserRepository.deactivate(user)
        UserService.send_email_activation(user, request)

    @staticmethod
    def send_email_activation(user: User, request=None):
        try:
            token = ActivationTokenService.generate(user)
            ActivationEmailService.send_email(user=user, token=token, request=request)
        except Exception:
            logging.exception(
                "Falha ao enviar e-mail de ativacao para user_pk=%s", user.pk
            )

    @staticmethod
    def activate_account(token: str) -> User:
        user_id, email = ActivationTokenService.validate(token)
        user = UserRepository.get_by_user_id(user_id)

        if user is None:
            raise ValidationError("Usuário do link de ativação não encontrado")

        if user.email.lower() != email.lower():
            raise ValidationError("Link de ativação inválido para este usuário")

        if user.is_active:
            return user

        UserRepository.activate(user)
        return user

    @staticmethod
    def delete_account(*, user: User) -> None:
        if not user.is_active:
            return
        UserRepository.deactivate(user)
        logging.info("Conta desativada via soft delete. user_pk=%s", user.pk)


class BaseSignedTokenService:
    signer_salt_setting: str
    max_age_setting: str
    signature_expired_msg: str
    bad_signature_msg: str
    malformed_msg: str

    @classmethod
    def signer(cls) -> TimestampSigner:
        return TimestampSigner(salt=getattr(settings, cls.signer_salt_setting))

    @classmethod
    def generate(cls, user: User) -> str:
        payload = f"{user.pk}:{user.email}"
        return cls.signer().sign(payload)

    @classmethod
    def _unsign(cls, token: str) -> str:
        try:
            return cls.signer().unsign(
                token, max_age=getattr(settings, cls.max_age_setting)
            )

        except SignatureExpired as e:
            raise ValidationError(cls.signature_expired_msg) from e

        except BadSignature as e:
            raise ValidationError(cls.bad_signature_msg) from e

    @classmethod
    def _extract_payload(cls, unsigned: str) -> tuple[int, str]:
        try:
            user_id_str, email = unsigned.split(":", 1)
            return int(user_id_str), email
        except (TypeError, ValueError) as e:
            raise ValidationError(cls.malformed_msg) from e

    @classmethod
    def validate(cls, token: str) -> tuple[int, str]:
        unsigned = cls._unsign(token)
        return cls._extract_payload(unsigned)


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


class BaseEmailService:
    route_name: str
    missing_request_msg: str
    subject: str

    @classmethod
    def _build_url_with_token(cls, token: str, request=None) -> str:
        path = reverse(cls.route_name)
        query = urlencode({"token": token})

        if request is None:
            raise ValidationError(cls.missing_request_msg)
        return request.build_absolute_uri(f"{path}?{query}")

    @classmethod
    def build_url(cls, *, token: str, request=None) -> str:
        return cls._build_url_with_token(token=token, request=request)

    @classmethod
    def _send_text_email(cls, *, recipient: str, message: str) -> None:
        send_mail(
            subject=cls.subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )

    @classmethod
    def build_message(cls, *, user: User, url: str) -> str:
        raise NotImplementedError

    @classmethod
    def send_email(cls, *, user: User, token: str, request=None) -> None:
        url = cls.build_url(
            token=token,
            request=request,
        )
        message = cls.build_message(user=user, url=url)
        cls._send_text_email(recipient=user.email, message=message)


class ActivationEmailService(BaseEmailService):
    route_name = "accounts:activate"
    missing_request_msg = "Não foi possível montar URL de ativação sem request"
    subject = "Ative sua conta"

    @classmethod
    def build_message(cls, *, user: User, url: str) -> str:
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

    @classmethod
    def build_message(cls, *, user: User, url: str) -> str:
        return (
            f"Olá, {user.first_name or user.username}!\n\n"
            "Recebemos uma solicitação para redefinir sua senha.\n"
            "Acesse o link abaixo para continuar\n\n"
            f"{url}\n\n"
            "Se você não solicitou esse cadastro ignore esse e-mail."
        )
