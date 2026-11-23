"""Profile & location endpoints (UC-2, UC-7)."""

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_profile_service
from app.api.schemas import LocationUpdate, UserProfile, UserPublic, UserUpdate
from app.domain.identity import CurrentUser
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserProfile)
def get_me(
    user: CurrentUser = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
):
    return service.profile_with_wallet(user.id)


@router.patch("/me", response_model=UserProfile)
def update_me(
    data: UserUpdate,
    user: CurrentUser = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
):
    service.update_profile(user.id, **data.model_dump())
    return service.profile_with_wallet(user.id)


@router.put("/me/location", response_model=UserProfile)
def set_location(
    data: LocationUpdate,
    user: CurrentUser = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
):
    """Точка проживания заяляется пользователем и НЕ верифицируется (решение N-2)."""
    service.set_location(user.id, data.lat, data.lon, data.address_text)
    return service.profile_with_wallet(user.id)


@router.get("/me/history")
def get_history(
    user: CurrentUser = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
):
    return service.history(user.id)


@router.get("/{user_id}/public", response_model=UserPublic)
def public_profile(user_id: int, service: ProfileService = Depends(get_profile_service)):
    """Публичный профиль: имя, аватар, рейтинг. Телефон и адрес не раскрываются."""
    return service.public_profile(user_id)
