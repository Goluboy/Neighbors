"""Публичный список категорий и получение категории по slug."""

from app.persistence.models import Category


def test_list_categories_returns_only_active_in_sort_order(client, db_session):
    db_session.add_all(
        [
            Category(name="Уборка", slug="cleaning", is_active=True, sort_order=2),
            Category(name="Ремонт", slug="repair", is_active=True, sort_order=1),
            Category(name="Скрытая", slug="hidden", is_active=False, sort_order=0),
        ]
    )
    db_session.commit()

    response = client.get("/api/v1/categories")

    assert response.status_code == 200, response.text
    assert [category["slug"] for category in response.json()] == ["repair", "cleaning"]


def test_get_category_returns_active_category_without_auth(client, db_session):
    category = Category(name="Ремонт", slug="repair", is_active=True)
    db_session.add(category)
    db_session.commit()

    response = client.get("/api/v1/categories/repair")

    assert response.status_code == 200, response.text
    assert response.json()["id"] == category.id


def test_get_category_hides_inactive_and_unknown_categories(client, db_session):
    db_session.add(Category(name="Скрытая", slug="hidden", is_active=False))
    db_session.commit()

    for slug in ("hidden", "unknown"):
        response = client.get(f"/api/v1/categories/{slug}")

        assert response.status_code == 404, response.text
        assert response.json()["error"]["code"] == "NOT_FOUND"
