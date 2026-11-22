"""Wallet endpoints (UC-3, UC-5, UC-7). Баланс — учебная заглушка без реальных платежей."""

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_wallet_service
from app.api.schemas import TopUpRequest, TransactionOut, WalletOut
from app.domain.identity import CurrentUser
from app.services.wallet_service import WalletService

router = APIRouter(prefix="/wallet", tags=["wallet"])


@router.get("", response_model=WalletOut)
def get_wallet(
    user: CurrentUser = Depends(get_current_user),
    service: WalletService = Depends(get_wallet_service),
):
    return service.get_wallet(user.id)


@router.post("/top-up")
def top_up(
    data: TopUpRequest,
    user: CurrentUser = Depends(get_current_user),
    service: WalletService = Depends(get_wallet_service),
):
    return service.top_up(user.id, data.amount)


@router.get("/transactions", response_model=list[TransactionOut])
def transactions(
    type: str | None = None,
    cursor: str | None = None,
    limit: int = 20,
    user: CurrentUser = Depends(get_current_user),
    service: WalletService = Depends(get_wallet_service),
):
    rows, _ = service.list_transactions(user.id, type, cursor, limit)
    return rows
