from typing import Any

from django.contrib.auth.models import User

from .repositories import UserRepository


class UserService:
    @staticmethod
    def create_account(validated_data: dict[str, Any]) -> User:
        return UserRepository.create_user(**validated_data)
