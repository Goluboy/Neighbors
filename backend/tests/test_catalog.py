"""UC-3: витрина отдаёт distance_m и не раскрывает адрес владельца."""

from app.core.security import create_access_token
from app.domain.enums import ItemStatus
from app.persistence.models import Category, Item, User


def _user(db, phone: str, *, lat=None, lon=None) -> User:
    user = User(phone=phone, latitude=lat, longitude=lon)
    db.add(user)
    db.commit()
    return user


def test_local_catalog_returns_distance_without_address(client, db_session):
    owner = _user(db_session, "+79990000101", lat="55.751244", lon="37.618423")
    renter = _user(db_session, "+79990000102", lat="55.751244", lon="37.618423")
    category = Category(name="Ремонт", slug="repair")
    db_session.add(category)
    db_session.flush()
    item = Item(
        owner_id=owner.id,
        category_id=category.id,
        title="Дрель",
        deposit_amount="0",
        status=ItemStatus.available,
    )
    db_session.add(item)
    db_session.commit()

    response = client.get(
        "/api/v1/catalog",
        params={"mode": "local"},
        headers={"Authorization": f"Bearer {create_access_token(renter.id)}"},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["meta"]["mode"] == "local"
    assert len(body["items"]) == 1
    card = body["items"][0]
    assert card["id"] == item.id
    assert card["distance_m"] == 0
    assert "address_text" not in card
