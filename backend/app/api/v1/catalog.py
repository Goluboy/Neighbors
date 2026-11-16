"""Catalog / search endpoint (UC-3).

Логика выдачи:
- mode=local (по умолчанию): вещи в радиусе шаговой доступности от точки пользователя;
- локальная выдача пуста -> fallback на mode=city с явным флагом в meta;
- без точки проживания доступен только city.
В выдаче показывается distance_m, адрес владельца не раскрывается.
"""

from fastapi import APIRouter, Depends

from app.api.deps import get_catalog_service, get_current_user
from app.api.schemas import ItemOut
from app.domain.identity import CurrentUser
from app.services.catalog_service import CatalogService

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("")
def search_catalog(
    user: CurrentUser = Depends(get_current_user),
    service: CatalogService = Depends(get_catalog_service),
    category_id: int | None = None,
    q: str | None = None,
    radius_km: float | None = None,
    mode: str = "local",  # local | city
    availability: str | None = None,  # available | busy
    cursor: str | None = None,
    limit: int = 20,
):
    result = service.search(
        user,
        category_id=category_id,
        q=q,
        radius_km=radius_km,
        mode=mode,
        availability=availability,
        cursor=cursor,
        limit=limit,
    )
    items = [
        ItemOut.model_validate(item).model_copy(update={"distance_m": distance})
        for item, distance in result["items"]
    ]
    return {"items": items, "meta": result["meta"]}
