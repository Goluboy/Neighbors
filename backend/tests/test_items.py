"""UC-6: публикация объявления и запрет услуг/еды/медикаментов."""

from app.core.security import create_access_token
from app.persistence.models import Category, User


def _owner_and_category(db) -> tuple[User, Category]:
    owner = User(phone="+79990000201")
    category = Category(name="Ремонт", slug="repair")
    db.add_all([owner, category])
    db.commit()
    return owner, category


def _body(category: Category, title: str) -> dict:
    return {
        "title": title,
        "description": "Аккумуляторная, в кейсе",
        "category_id": category.id,
        "deposit_amount": "0",
        "format": "free",
    }


def test_create_item_returns_card(client, db_session):
    owner, category = _owner_and_category(db_session)

    response = client.post(
        "/api/v1/items",
        json=_body(category, "Дрель"),
        headers={"Authorization": f"Bearer {create_access_token(owner.id)}"},
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["title"] == "Дрель"
    assert body["category"]["slug"] == "repair"
    assert body["owner"]["id"] == owner.id


def test_prohibited_item_is_rejected(client, db_session):
    owner, category = _owner_and_category(db_session)

    response = client.post(
        "/api/v1/items",
        json=_body(category, "Готовлю еду на заказ"),
        headers={"Authorization": f"Bearer {create_access_token(owner.id)}"},
    )

    assert response.status_code == 422, response.text
    assert response.json()["error"]["code"] == "PROHIBITED_ITEM"
