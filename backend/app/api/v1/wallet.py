"""Wallet endpoints (UC-3, UC-5, UC-7). Баланс — учебная заглушка без реальных платежей."""

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.api.schemas import TopUpRequest, TransactionOut, WalletOut
from app.domain.identity import CurrentUser

router = APIRouter(prefix="/wallet", tags=["wallet"])


@router.get("", response_model=WalletOut)
def get_wallet(user: CurrentUser = Depends(get_current_user)):
    raise NotImplementedError  # { total, held, available }


@router.post("/top-up")
def top_up(data: TopUpRequest, user: CurrentUser = Depends(get_current_user)):
    raise NotImplementedError  # заглушка пополнения


@router.get("/transactions", response_model=list[TransactionOut])
def transactions(
    type: str | None = None,
    cursor: str | None = None,
    user: CurrentUser = Depends(get_current_user),
):
    raise NotImplementedError
