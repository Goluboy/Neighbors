"""Auth endpoints (UC-1): верификация только по номеру телефона."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.composition.container import get_sms_sender
from app.core.config import settings
from app.core.database import get_db
from app.domain.ports.repositories import SmsSenderPort
from app.infrastructure.sms import generate_code
from app.schemas import SendCodeRequest, TokenResponse, VerifyCodeRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/phone/send-code", status_code=202)
def send_code(data: SendCodeRequest, sms: SmsSenderPort = Depends(get_sms_sender)):
    """Запрос SMS-кода. Повторная отправка ограничена таймаутом (TODO: rate-limit в Redis)."""
    # TODO(UC-1): кодогенерация и cooldown переедут в AuthService
    code = generate_code(stub_mode=settings.SMS_PROVIDER == "stub")
    sms.send(data.phone, f"Ваш код подтверждения: {code}")
    return {"detail": "code_sent"}


@router.post("/phone/verify", response_model=TokenResponse)
def verify_code(data: VerifyCodeRequest, db: Session = Depends(get_db)):
    """Подтверждение кода -> JWT. При повторном входе авторизует существующий аккаунт."""
    # TODO: AuthService.verify_and_login + поиск/создание User + Wallet, генерация токенов
    raise NotImplementedError("каркас: реализовать UC-1")
