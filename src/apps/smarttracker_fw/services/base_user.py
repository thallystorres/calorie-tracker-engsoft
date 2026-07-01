from django.contrib.auth.models import User


class BaseUserService:
    def create_account(self, validated_data: dict, request=None) -> User:
        pass

    def update_account(
        self, user: User, validated_data: dict, request=None
    ) -> tuple[User, bool]:
        pass

    def authenticate_account(self, username_or_email: str, password: str) -> User:
        pass

    def activate_account(self, token: str) -> User:
        pass

    def delete_account(self, user: User) -> None:
        pass

    def request_password_reset(self, email: str, request=None) -> None:
        pass

    def reset_password_with_token(self, token: str, new_password: str) -> User:
        pass
