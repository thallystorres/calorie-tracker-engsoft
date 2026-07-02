from functools import cache

from core.auth.dependencies import get_base_user_service

from .repositories import UserRepository
from .services import (
    UserService,
)


@cache
def get_user_repository() -> UserRepository:
    return UserRepository()


@cache
# Gambiarra pra manter compatibilidade
def get_user_service() -> UserService:
    user_service = get_base_user_service()
    user_service.__class__ = UserService
    return user_service
