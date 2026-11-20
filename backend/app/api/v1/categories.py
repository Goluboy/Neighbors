"""Categories endpoints (публичные, кэшируемые)."""

from fastapi import APIRouter, Depends

from app.api.deps import get_category_service
from app.api.schemas import CategoryOut
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
def list_categories(service: CategoryService = Depends(get_category_service)):
    return service.list_categories()


@router.get("/{slug}", response_model=CategoryOut)
def get_category(slug: str, service: CategoryService = Depends(get_category_service)):
    return service.get_category(slug)
