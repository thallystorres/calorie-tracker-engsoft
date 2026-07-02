from functools import cache

from core.notifications.services import ActivationEmailService, PasswordResetEmailService

from .repositories import BaseUserRepository
from .services import (
    ActivationTokenService,
    BaseUserService,
    PasswordResetTokenService,
)

@cache
def get_base_user_repository() -> BaseUserRepository:
    return BaseUserRepository()

@cache
def get_base_user_service() -> BaseUserService:
    return BaseUserService(
        user_repository=get_base_user_repository(),
        activation_token_service=ActivationTokenService(),
        password_reset_token_service=PasswordResetTokenService(),
        activation_email_service=ActivationEmailService(),
        password_reset_email_service=PasswordResetEmailService(),
    )
