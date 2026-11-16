"""Items endpoints (UC-6): публикация и управление объявлениями."""

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_item_service
from app.api.schemas import ItemCreate, ItemOut, ItemUpdate
from app.domain.identity import CurrentUser
from app.services.item_service import ItemService

router = APIRouter(prefix="/items", tags=["items"])


@router.post("", response_model=ItemOut, status_code=201)
def create_item(
    data: ItemCreate,
    user: CurrentUser = Depends(get_current_user),
    service: ItemService = Depends(get_item_service),
):
    """Только физические предметы; услуги/еда/медикаменты запрещены (стоп-слова + модерация)."""
    return service.create_item(
        user.id,
        title=data.title,
        description=data.description,
        category_id=data.category_id,
        deposit_amount=data.deposit_amount,
        rental_format=data.format,
    )


@router.get("/me")
def my_items(
    status: str | None = None,
    user: CurrentUser = Depends(get_current_user),
):
    raise NotImplementedError


@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: int, user: CurrentUser = Depends(get_current_user)):
    """Карточка: фото, описание, залог, рейтинг владельца, расстояние (не адрес)."""
    raise NotImplementedError


@router.patch("/{item_id}", response_model=ItemOut)
def update_item(
    item_id: int,
    data: ItemUpdate,
    user: CurrentUser = Depends(get_current_user),
    service: ItemService = Depends(get_item_service),
):
    return service.update_item(item_id, user.id, **data.model_dump())


@router.post("/{item_id}/hide")
def hide_item(
    item_id: int,
    user: CurrentUser = Depends(get_current_user),
    service: ItemService = Depends(get_item_service),
):
    """Скрытие из выдачи; активные заказы продолжают выполняться."""
    return service.hide(item_id, user.id)


@router.post("/{item_id}/show")
def show_item(
    item_id: int,
    user: CurrentUser = Depends(get_current_user),
    service: ItemService = Depends(get_item_service),
):
    return service.show(item_id, user.id)


@router.delete("/{item_id}", status_code=204)
def delete_item(
    item_id: int,
    user: CurrentUser = Depends(get_current_user),
    service: ItemService = Depends(get_item_service),
):
    service.delete(item_id, user.id)


@router.post("/{item_id}/photos")
def upload_photo(item_id: int, user: CurrentUser = Depends(get_current_user)):
    """multipart-загрузка через бэкенд -> S3-совместимое хранилище (SeaweedFS): валидация размера/типа, сжатие."""
    raise NotImplementedError


@router.delete("/{item_id}/photos/{photo_id}", status_code=204)
def delete_photo(item_id: int, photo_id: int, user: CurrentUser = Depends(get_current_user)):
    raise NotImplementedError
