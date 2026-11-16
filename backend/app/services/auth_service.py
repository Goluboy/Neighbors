"""Use-case сервис авторизации (UC-1): верификация только по номеру телефона."""

from collections.abc import Callable

from app.core.config import settings
from app.core.exceptions import DomainError
from app.core.security import create_access_token, create_refresh_token
from app.domain.ports.repositories import (
    CodeStoragePort,
    SmsSenderPort,
    UserRepository,
    WalletRepository,
)


class InvalidCodeError(DomainError):
    """Неверный или истёкший код подтверждения."""

    code = "INVALID_CODE"
    http_status = 400


class ResendTooSoonError(DomainError):
    """Повторная отправка ограничена таймаутом (бизнес-правило UC-1)."""

    code = "RESEND_TOO_SOON"
    http_status = 429


class AuthService:
    SMS_COOLDOWN_SECONDS = 60

    def __init__(
        self,
        *,
        uow,
        users: UserRepository,
        wallets: WalletRepository,
        sms: SmsSenderPort,
        codes: CodeStoragePort,
        new_code: Callable[[], str],
    ):
        self.uow = uow
        self.users = users
        self.wallets = wallets
        self.sms = sms
        self.codes = codes
        self.new_code = new_code

    def send_code(self, phone: str) -> None:
        if not self.codes.can_resend(phone, self.SMS_COOLDOWN_SECONDS):
            raise ResendTooSoonError("Код уже отправлен, попробуйте позже")
        code = self.new_code()
        self.codes.save(phone, code, settings.VERIFICATION_CODE_TTL_SECONDS)
        self.sms.send(phone, f"Ваш код подтверждения: {code}")

    def verify_and_login(self, phone: str, code: str):
        """Проверяет код; при повторном входе авторизует существующий аккаунт (UC-1 правило)."""
        if not self.codes.check_and_consume(phone, code, settings.VERIFICATION_MAX_ATTEMPTS):
            raise InvalidCodeError("Неверный или истёкший код")

        user = self.users.get_by_phone(phone)
        is_new = user is None
        if is_new:
            user = self.users.add(dict(phone=phone))
            self.wallets.add(dict(user_id=user.id, total_balance=0, held_balance=0))
            self.uow.commit()
        assert user is not None
        return {
            "access_token": create_access_token(user.id),
            "refresh_token": create_refresh_token(user.id),
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "is_new_user": is_new,
            "user": user,
        }
