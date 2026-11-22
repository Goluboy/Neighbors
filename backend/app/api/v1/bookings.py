"""Bookings endpoints (UC-3, UC-4, UC-5).

Жизненный цикл: pending -> approved/rejected -> rented -> returned/disputed/cancelled
"""

from typing import Literal

from fastapi import APIRouter, Depends

from app.api.deps import get_booking_service, get_current_user
from app.api.schemas import BookingCreate, BookingOut
from app.domain.identity import CurrentUser
from app.services.booking_service import BookingService

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("", response_model=BookingOut, status_code=201)
def create_booking(
    data: BookingCreate,
    user: CurrentUser = Depends(get_current_user),
    service: BookingService = Depends(get_booking_service),
):
    """Создать заявку. Атомарно холдирует залог (если > 0); при нехватке средств — 400."""
    return service.create_booking(user.id, data.item_id, data.start_date, data.end_date)


@router.get("/me", response_model=list[BookingOut])
def my_bookings(
    as_role: Literal["renter", "owner"] = "renter",
    status: str | None = None,
    user: CurrentUser = Depends(get_current_user),
    service: BookingService = Depends(get_booking_service),
):
    return service.list_for_user(user.id, as_role, status)


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(
    booking_id: int,
    user: CurrentUser = Depends(get_current_user),
    service: BookingService = Depends(get_booking_service),
):
    return service.get_booking(booking_id, user.id)


# --- действия владельца ---
@router.post("/{booking_id}/approve", response_model=BookingOut)
def approve(
    booking_id: int,
    user: CurrentUser = Depends(get_current_user),
    service: BookingService = Depends(get_booking_service),
):
    return service.approve(booking_id, user.id)


@router.post("/{booking_id}/reject", response_model=BookingOut)
def reject(
    booking_id: int,
    user: CurrentUser = Depends(get_current_user),
    service: BookingService = Depends(get_booking_service),
):
    return service.reject(booking_id, user.id)


@router.post("/{booking_id}/confirm-return", response_model=BookingOut)
def confirm_return(
    booking_id: int,
    user: CurrentUser = Depends(get_current_user),
    service: BookingService = Depends(get_booking_service),
):
    """Вещь получена без повреждений -> разморозка залога, статус returned."""
    return service.confirm_return(booking_id, user.id)


@router.post("/{booking_id}/report-issue", response_model=BookingOut)
def report_issue(
    booking_id: int,
    reason: str,
    user: CurrentUser = Depends(get_current_user),
    service: BookingService = Depends(get_booking_service),
):
    """Порча вещи -> спорная ситуация, разморозка заблокирована, подключается модератор."""
    return service.report_issue(booking_id, user.id, reason)


# --- действия арендатора ---
@router.post("/{booking_id}/cancel", response_model=BookingOut)
def cancel(
    booking_id: int,
    user: CurrentUser = Depends(get_current_user),
    service: BookingService = Depends(get_booking_service),
):
    """Отмена до ответа владельца: залог -> release, вещь -> available."""
    return service.cancel_by_renter(booking_id, user.id)


@router.post("/{booking_id}/confirm-receipt", response_model=BookingOut)
def confirm_receipt(
    booking_id: int,
    user: CurrentUser = Depends(get_current_user),
    service: BookingService = Depends(get_booking_service),
):
    """«Вещь у меня, всё отлично» -> старт таймера аренды."""
    return service.confirm_receipt(booking_id, user.id)


@router.post("/{booking_id}/refuse-on-inspection", response_model=BookingOut)
def refuse_on_inspection(
    booking_id: int,
    user: CurrentUser = Depends(get_current_user),
    service: BookingService = Depends(get_booking_service),
):
    """Отказ при осмотре: залог release, сделка аннулируется."""
    return service.refuse_on_inspection(booking_id, user.id)


@router.post("/{booking_id}/initiate-return", response_model=BookingOut)
def initiate_return(
    booking_id: int,
    user: CurrentUser = Depends(get_current_user),
    service: BookingService = Depends(get_booking_service),
):
    """Уведомление владельцу о готовности вернуть."""
    return service.initiate_return(booking_id, user.id)


# --- оценки (UC-5) ---
@router.post("/{booking_id}/reviews")
def leave_review(booking_id: int, user: CurrentUser = Depends(get_current_user)):
    """Оценка 1-5 + отзыв. Не публикуется второй стороне до встречной оценки или истечения срока."""
    raise NotImplementedError


@router.get("/{booking_id}/reviews")
def booking_reviews(booking_id: int, user: CurrentUser = Depends(get_current_user)):
    raise NotImplementedError
