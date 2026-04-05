from django.contrib.auth.models import User


class UserRepository:
    @staticmethod
    def exists_by_username(username: str) -> bool:
        return User.objects.filter(username=username).exists()

    @staticmethod
    def exists_by_email(email: str) -> bool:
        return User.objects.filter(email_iexact=email).exists()

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
