from typing import Any

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from src.apps.accounts.services import UserService

from .repositories import UserRepository


def _run_password_validators(password: str, user: User | None = None) -> None:
    try:
        validate_password(password=password, user=user)
    except DjangoValidationError as e:
        raise serializers.ValidationError(e.messages)


class AccountRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "confirm_password",
        )

    def validate_username(self, value: str) -> str:
        msg = "Nome do usuário já está em uso"
        if UserRepository.exists_by_username(value):
            raise serializers.ValidationError(msg)
        return value

    def validate_email(self, value: str) -> str:
        msg = "E-mail já está em uso."
        email = value.strip().lower()
        if UserRepository.exists_by_email(email):
            raise serializers.ValidationError(msg)
        return email

    def validate(self, attrs: dict[str, str]) -> dict[str, str]:
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "As senhas não conferem."}
            )

        attrs.pop("confirm_password")
        _run_password_validators(attrs["password"], User(**attrs))

        return attrs


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")
        read_only_fields = ("id", "username")

    def validate_email(self, value: str) -> str:
        msg = "E-mail já está em uso."
        email = value.strip().lower()
        user = self.instance
        if user is None:
            return email
        if UserRepository.exists_by_email(email, user.id):
            raise serializers.ValidationError(msg)
        return email


class AccountLoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        username_or_email = attrs["username_or_email"].strip()
        password = attrs["password"]

        user = UserService.authenticate_account(
            username_or_email=username_or_email, password=password
        )
        attrs["user"] = user
        return attrs
