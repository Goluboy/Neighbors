"""Auth endpoints (UC-1): верификация только по номеру телефона."""

from fastapi import APIRouter, Depends

from app.api.deps import get_auth_service
from app.api.schemas import SendCodeRequest, TokenResponse, VerifyCodeRequest
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/phone/send-code", status_code=202)
def send_code(data: SendCodeRequest, service: AuthService = Depends(get_auth_service)):
    """Запрос SMS-кода. Повторная отправка ограничена таймаутом."""
    service.send_code(data.phone)
    return {"detail": "code_sent"}


@router.post("/phone/verify", response_model=TokenResponse)
def verify_code(data: VerifyCodeRequest, service: AuthService = Depends(get_auth_service)):
    """Подтверждение кода -> JWT. При повторном входе авторизует существующий аккаунт."""
    return service.verify_and_login(data.phone, data.code)
