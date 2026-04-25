from functools import cache

from .repositories import UserRepository
from .services import (
    ActivationEmailService,
    ActivationTokenService,
    PasswordResetEmailService,
    PasswordResetTokenService,
    UserService,
)


@cache
def get_user_repository() -> UserRepository:
    return UserRepository()


@cache
def get_user_service() -> UserService:
    return UserService(
        user_repository=get_user_repository(),
        activation_token_service=ActivationTokenService(),
        password_reset_token_service=PasswordResetTokenService(),
        activation_email_service=ActivationEmailService(),
        password_reset_email_service=PasswordResetEmailService(),
    )
