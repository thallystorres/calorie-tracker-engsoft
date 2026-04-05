from django.contrib.auth.models import User


class UserRepository:
    @staticmethod
    def exists_by_username(username: str) -> bool:
        return User.objects.filter(username=username).exists()

    @staticmethod
    def exists_by_email(email: str) -> bool:
        return User.objects.filter(email__iexact=email).exists()

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
    def create_user(
        *, username: str, email: str, first_name: str, last_name: str, password: str
    ) -> User:
        return User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
