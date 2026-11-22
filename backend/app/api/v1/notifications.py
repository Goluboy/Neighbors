"""Notifications endpoints (UC-8)."""

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_notification_service
from app.api.schemas import NotificationOut
from app.domain.identity import CurrentUser
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationOut])
def list_notifications(
    cursor: str | None = None,
    limit: int = 20,
    user: CurrentUser = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    rows, _ = service.list_notifications(user.id, cursor, limit)
    return rows


@router.post("/read")
def mark_read(
    ids: list[int] | None = None,
    all_: bool = False,
    user: CurrentUser = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    service.mark_read(user.id, ids, all_)


@router.get("/settings")
def get_settings_endpoint(user: CurrentUser = Depends(get_current_user)):
    raise NotImplementedError


@router.put("/settings")
def update_settings(user: CurrentUser = Depends(get_current_user)):
    raise NotImplementedError  # настройки применяются к новым событиям
