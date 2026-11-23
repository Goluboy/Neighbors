"""Use-case сервис публичного справочника категорий."""

from app.core.exceptions import NotFoundError
from app.domain.ports.repositories import CategoryRepository


class CategoryService:
    def __init__(self, *, categories: CategoryRepository):
        self.categories = categories

    def list_categories(self):
        return self.categories.list_active()

    def get_category(self, slug: str):
        category = self.categories.get_by_slug(slug)
        if category is None or not category.is_active:
            raise NotFoundError("Категория не найдена")
        return category
