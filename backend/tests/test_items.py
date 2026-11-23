"""UC-6: публикация объявления и запрет услуг/еды/медикаментов."""

from app.core.security import create_access_token
from app.domain.enums import ItemStatus
from app.persistence.models import Category, Item, User


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


def _create_item(db, owner: User, category: Category, status: ItemStatus) -> Item:
    item = Item(
        owner_id=owner.id,
        category_id=category.id,
        title="Дрель",
        description="Аккумуляторная",
        deposit_amount="0",
        status=status,
    )
    db.add(item)
    db.commit()
    return item


def _headers(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}


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


def test_my_items_returns_only_owners_items_and_filters_status(client, db_session):
    owner, category = _owner_and_category(db_session)
    other_owner = User(phone="+79990000202")
    db_session.add(other_owner)
    db_session.commit()
    available = _create_item(db_session, owner, category, ItemStatus.available)
    hidden = _create_item(db_session, owner, category, ItemStatus.hidden)
    other_item = _create_item(db_session, other_owner, category, ItemStatus.available)

    response = client.get("/api/v1/items/me", headers=_headers(owner))

    assert response.status_code == 200, response.text
    assert {item["id"] for item in response.json()} == {available.id, hidden.id}
    assert other_item.id not in {item["id"] for item in response.json()}

    response = client.get(
        "/api/v1/items/me",
        params={"status": "hidden"},
        headers=_headers(owner),
    )

    assert response.status_code == 200, response.text
    assert [item["id"] for item in response.json()] == [hidden.id]


def test_my_items_requires_authentication(client):
    response = client.get("/api/v1/items/me")

    assert response.status_code == 401


def test_my_items_rejects_unknown_status(client, db_session):
    owner, _ = _owner_and_category(db_session)

    response = client.get(
        "/api/v1/items/me",
        params={"status": "unknown"},
        headers=_headers(owner),
    )

    assert response.status_code == 422


def test_get_item_hides_hidden_item_from_non_owner(client, db_session):
    owner, category = _owner_and_category(db_session)
    other_user = User(phone="+79990000203")
    db_session.add(other_user)
    db_session.commit()
    item = _create_item(db_session, owner, category, ItemStatus.hidden)

    owner_response = client.get(f"/api/v1/items/{item.id}", headers=_headers(owner))
    other_response = client.get(f"/api/v1/items/{item.id}", headers=_headers(other_user))

    assert owner_response.status_code == 200, owner_response.text
    assert owner_response.json()["status"] == "hidden"
    assert "address_text" not in owner_response.json()["owner"]
    assert other_response.status_code == 404, other_response.text
    assert other_response.json()["error"]["code"] == "NOT_FOUND"


def test_get_item_returns_available_item_to_another_user(client, db_session):
    owner, category = _owner_and_category(db_session)
    other_user = User(phone="+79990000204")
    db_session.add(other_user)
    db_session.commit()
    item = _create_item(db_session, owner, category, ItemStatus.available)

    response = client.get(f"/api/v1/items/{item.id}", headers=_headers(other_user))

    assert response.status_code == 200, response.text
    assert response.json()["id"] == item.id
    assert response.json()["title"] == item.title
    assert "address_text" not in response.json()["owner"]


def test_get_item_returns_404_for_missing_item(client, db_session):
    user, _ = _owner_and_category(db_session)

    response = client.get("/api/v1/items/999999", headers=_headers(user))

    assert response.status_code == 404, response.text
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_get_item_requires_authentication(client, db_session):
    owner, category = _owner_and_category(db_session)
    item = _create_item(db_session, owner, category, ItemStatus.available)

    response = client.get(f"/api/v1/items/{item.id}")

    assert response.status_code == 401
