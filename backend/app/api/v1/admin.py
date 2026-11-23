"""Admin/moderation endpoints (UC-9, UC-10). Требует роль moderator."""

from fastapi import APIRouter, Depends

from app.api.deps import get_admin_service, require_moderator
from app.api.schemas import DisputeResolve
from app.domain.identity import CurrentUser
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_moderator)])


# --- споры по заказам (UC-9) ---
@router.get("/disputes")
def list_disputes(
    status: str = "pending",
    service: AdminService = Depends(get_admin_service),
):
    return service.list_disputes(status)


@router.get("/disputes/{dispute_id}")
def dispute_context(dispute_id: int):
    """Контекст: переписка чата, история заказа, карточка вещи, заявленная проблема."""
    raise NotImplementedError


@router.post("/disputes/{dispute_id}/resolve")
def resolve_dispute(
    dispute_id: int, data: DisputeResolve, mod: CurrentUser = Depends(require_moderator)
):
    """refund (разморозка в пользу арендатора) | charge (списание владельцу) | dismiss.
    Опционально ban_user. Из 'disputed' заказ выходит только решением модератора."""
    raise NotImplementedError


# --- жалобы на контент (UC-10) ---
@router.get("/reports")
def list_reports():
    raise NotImplementedError


@router.post("/reports/{report_id}/resolve")
def resolve_report(report_id: int, action: str, comment: str = ""):
    raise NotImplementedError  # hide_item | delete_message | dismiss | ban


# --- пользователи ---
@router.post("/users/{user_id}/ban")
def ban_user(user_id: int, reason: str = ""):
    raise NotImplementedError  # причина видна заблокированному пользователю


@router.post("/users/{user_id}/unban")
def unban_user(user_id: int):
    raise NotImplementedError


# --- категории (CRUD) ---
@router.post("/categories")
def create_category(name: str, slug: str):
    raise NotImplementedError
