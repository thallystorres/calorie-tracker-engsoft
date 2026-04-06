from typing import Any

from django.contrib.auth.models import User


class UserRepository:
    @staticmethod
    def exists_by_username(username: str) -> bool:
        return User.objects.filter(username=username).exists()

    @staticmethod
    def exists_by_email(email: str, user_id: int | None = None) -> bool:
        qs = User.objects.filter(email__iexact=email)
        if user_id is not None:
            qs = qs.exclude(id=user_id)
        return qs.exists()

    @staticmethod
    def get_by_user_id(user_id: int) -> User | None:
        return User.objects.filter(pk=user_id).first()

    @staticmethod
    def get_by_username(username: str) -> User | None:
        return User.objects.filter(username=username).first()

    @staticmethod
    def get_by_email(email: str) -> User | None:
        return User.objects.filter(email__iexact=email).first()

    @staticmethod
    def get_by_username_or_email(identifier: str) -> User | None:
        user = UserRepository.get_by_username(identifier)
        if user is not None:
            return user
        return UserRepository.get_by_email(identifier)

    @staticmethod
    def activate(user: User) -> None:
        user.is_active = True
        user.save()

    @staticmethod
    def update_user(*, user: User, data: dict[str, Any]) -> User:
        update_fields = ("email", "first_name", "last_name")
        for field in update_fields:
            if field in data:
                setattr(user, field, data[field])
        user.save(update_fields=update_fields)
        return user

    @staticmethod
    def create_user(
        *, username: str, email: str, first_name: str, last_name: str, password: str
    ) -> User:
        return User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            is_active=False,
        )
