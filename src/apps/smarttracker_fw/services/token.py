from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.signing import BadSignature, SignatureExpired, TimestampSigner


class BaseSignedTokenService:
    signer_salt_setting: str
    max_age_setting: str
    signature_expired_msg: str
    bad_signature_msg: str
    malformed_msg: str

    def signer(self) -> TimestampSigner:
        return TimestampSigner(salt=getattr(settings, self.signer_salt_setting))

    def generate(self, user: User) -> str:
        payload = f"{user.pk}:{user.email}"
        return self.signer().sign(payload)

    def _unsign(self, token: str) -> str:
        try:
            return self.signer().unsign(
                token, max_age=getattr(settings, self.max_age_setting)
            )

        except SignatureExpired as e:
            raise ValidationError(self.signature_expired_msg) from e

        except BadSignature as e:
            raise ValidationError(self.bad_signature_msg) from e

    def _extract_payload(self, unsigned: str) -> tuple[int, str]:
        try:
            user_id_str, email = unsigned.split(":", 1)
            return int(user_id_str), email
        except (TypeError, ValueError) as e:
            raise ValidationError(self.malformed_msg) from e

    def validate(self, token: str) -> tuple[int, str]:
        unsigned = self._unsign(token)
        return self._extract_payload(unsigned)


class ActivationTokenService(BaseSignedTokenService):
    signer_salt_setting = "ACCOUNT_ACTIVATION_SALT"
    max_age_setting = "ACCOUNT_ACTIVATION_MAX_AGE_SECONDS"
    signature_expired_msg = "Link de ativação expirado."
    bad_signature_msg = "Link de ativação inválido."
    malformed_msg = "Token de ativação malformado."


class PasswordResetTokenService(BaseSignedTokenService):
    signer_salt_setting = "PASSWORD_RESET_SALT"
    max_age_setting = "PASSWORD_RESET_MAX_AGE_SECONDS"
    signature_expired_msg = "Token de redefinição expirado."
    bad_signature_msg = "Token de redefinição inválido."
    malformed_msg = "Token de redefinição malformado."
