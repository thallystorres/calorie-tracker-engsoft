from typing import Any

from django.contrib.auth.models import User
from rest_framework.exceptions import AuthenticationFailed

from .repositories import UserRepository


class UserService:
    @staticmethod
    def create_account(validated_data: dict[str, Any]) -> User:
        return UserRepository.create_user(**validated_data)

    @staticmethod
    def authenticate_account(*, username_or_email: str, password: str):
        msg = "Credenciais inválidas."
        user = UserRepository.get_by_username_or_email(username_or_email)

        if user is None or not user.check_password(password) or not user.is_active:
            raise AuthenticationFailed(msg)

        return user

    @staticmethod
    def update_account_profile(*, user: User, validated_data: dict[str, Any]) -> User:
        return UserRepository.update_user(user=user, data=validated_data)
