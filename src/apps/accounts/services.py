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

logger = logging.getLogger(__name__)


class UserService:
    @staticmethod
    def create_account(validated_data: dict[str, Any], request=None) -> User:
        user = UserRepository.create_user(**validated_data)
        try:
            token = ActivationTokenService.generate(user)
            EmailService.send_activation_email(user=user, token=token, request=request)
        except Exception:
            logger.exception(
                "Falha ao enviar e-mail de ativacao para user_pk=%s", user.pk
            )
        return user

    @staticmethod
    def authenticate_account(*, username_or_email: str, password: str):
        invalid_credentials_msg = "Credenciais inválidas."
        not_active_msg = "Conta não verificada. Verifique seu e-mail para ativar"
        user = UserRepository.get_by_username_or_email(username_or_email)

        if user is None or not user.check_password(password):
            raise AuthenticationFailed(invalid_credentials_msg)

        if not user.is_active:
            raise AuthenticationFailed(not_active_msg)

        return user

    @staticmethod
    def update_account_profile(*, user: User, validated_data: dict[str, Any]) -> User:
        return UserRepository.update_user(user=user, data=validated_data)

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


class ActivationTokenService:
    _signer = TimestampSigner(salt=settings.ACCOUNT_ACTIVATION_SALT)

    @staticmethod
    def generate(user: User) -> str:
        payload = f"{user.pk}:{user.email}"
        return ActivationTokenService._signer.sign(payload)

    @staticmethod
    def validate(token: str) -> tuple[int, str]:
        unsigned = ActivationTokenService._unsign(token)
        return ActivationTokenService._extract_payload(unsigned)

    @staticmethod
    def _unsign(token: str) -> str:
        try:
            return ActivationTokenService._signer.unsign(
                token, max_age=settings.ACCOUNT_ACTIVATION_MAX_AGE_SECONDS
            )

        except SignatureExpired as e:
            raise ValidationError("Link de ativação expirado.") from e

        except BadSignature as e:
            raise ValidationError("Link de ativação inválido.") from e

    @staticmethod
    def _extract_payload(unsigned: str) -> tuple[int, str]:
        try:
            user_id_str, email = unsigned.split(":", 1)
            return int(user_id_str), email
        except (TypeError, ValueError) as exc:
            raise ValidationError("Token de ativação malformado.") from exc


class EmailService:
    @staticmethod
    def build_activation_url(*, token: str, request=None) -> str:
        path = reverse("accounts:activate")
        query = urlencode({"token": token})

        if request is None:
            raise ValidationError(
                "Não foi possível montar URL de ativação sem request"
                " ou ACCOUNT_ACTIVATION_BASE_URL."
            )
        return request.build_absolute_uri(f"{path}?{query}")

    @staticmethod
    def send_activation_email(*, user: User, token: str, request=None) -> None:
        activation_url = EmailService.build_activation_url(token=token, request=request)
        subject = "Ative sua conta"
        message = (
            f"Olá, {user.first_name or user.username}!\n\n"
            "Seu cadastro foi realizado com sucesso.\n"
            "Para ativar sua conta acesse o link abaixo:\n\n"
            f"{activation_url}\n\n"
            "Se você não solicitou esse cadastro ignore esse e-mail."
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
