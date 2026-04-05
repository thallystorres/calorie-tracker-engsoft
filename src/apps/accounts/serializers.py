from django.contrib.auth.models import User
from rest_framework import serializers

from .repositories import UserRepository


class AccountRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
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
        msg = "E-mail já está em uso"
        if UserRepository.exists_by_email(value):
            raise serializers.ValidationError(msg)
        return value


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
        if User.objects.exclude(id=user.id).filter(email__iexact=email).exists():
            raise serializers.ValidationError(msg)
        return email
