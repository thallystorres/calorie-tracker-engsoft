from abc import ABC, abstractmethod

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.urls import reverse


class BaseEmailService(ABC):
    route_name: str
    missing_request_msg: str
    subject: str

    def _build_url_with_token(self, token: str, request=None) -> str:
        if request is None:
            raise ValidationError(self.missing_request_msg)
        path = reverse(self.route_name, kwargs={"token": token})
        return request.build_absolute_uri(path)

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
    route_name = "accounts-ui:verify-email"
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
    route_name = "accounts-ui:password-reset-confirm"
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


class SimpleEmailService(BaseEmailService):
    route_name = ""
    missing_request_msg = ""
    subject = ""

    def build_url(self, *, token: str, request=None) -> str:
        return ""

    def send_email(self, *, user: User, token: str = "", request=None) -> None:
        message = self.build_message(user=user, url="")
        self._send_text_email(recipient=user.email, message=message)


class ReminderEmailService(SimpleEmailService):
    subject = "Lembrete de registro de refeicao"

    def build_message(self, *, user: User, url: str) -> str:
        return (
            f"Olá, {user.first_name or user.username}!\n\n"
            "Notamos que voce esta sem registrar refeicoes nas ultimas horas.\n"
            "Acesse o sistema e registre sua refeicao.\n\n"
            "Se voce ja registrou recentemente, por favor desconsidere."
        )


class ExcessEmailService(SimpleEmailService):
    subject = "Alerta de excesso de calorias"

    def build_message(self, *, user: User, url: str) -> str:
        return (
            f"Olá, {user.first_name or user.username}!\n\n"
            "Seu consumo de calorias hoje atingiu ou ultrapassou sua meta diaria.\n"
            "Acesse o sistema para revisar seus registros.\n\n"
            "Continue firme no seu objetivo!"
        )
