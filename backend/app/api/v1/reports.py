"""Reports endpoints (UC-10). Автор жалобы скрыт от целевого пользователя."""

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.api.schemas import ReportCreate
from app.domain.identity import CurrentUser

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", status_code=202)
def create_report(data: ReportCreate, user: CurrentUser = Depends(get_current_user)):
    raise NotImplementedError  # создать Dispute(item|message|user), пометить цель


@router.get("/me")
def my_reports(user: CurrentUser = Depends(get_current_user)):
    raise NotImplementedError
