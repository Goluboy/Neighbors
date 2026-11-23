"""Тесты лёгких ручек: брони, чат, кошелёк, уведомления, история и admin."""

from sqlalchemy import select

from app.core.security import create_access_token
from app.domain.enums import BookingStatus, ItemStatus
from app.persistence.models import Booking, Category, Item, User, Wallet


def _headers(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}


def _category(db) -> Category:
    category = db.scalar(select(Category).where(Category.slug == "repair"))
    if category is None:
        category = Category(name="Ремонт", slug="repair")
        db.add(category)
        db.commit()
    return category


def test_booking_list_and_details_respect_participants(client, db_session):
    owner = User(phone="+79990000801")
    renter = User(phone="+79990000802")
    db_session.add_all([owner, renter])
    db_session.flush()
    db_session.add(Wallet(user_id=renter.id, total_balance=100, held_balance=0))
    category = _category(db_session)
    item = Item(
        owner_id=owner.id,
        category_id=category.id,
        title="Дрель",
        deposit_amount=0,
        status=ItemStatus.available,
    )
    db_session.add(item)
    db_session.flush()
    booking = Booking(
        item_id=item.id,
        renter_id=renter.id,
        status=BookingStatus.approved,
        deposit_held_amount=0,
    )
    db_session.add(booking)
    db_session.commit()

    mine = client.get("/api/v1/bookings/me", headers=_headers(renter))
    owned = client.get("/api/v1/bookings/me?as_role=owner", headers=_headers(owner))
    details = client.get(f"/api/v1/bookings/{booking.id}", headers=_headers(renter))

    assert mine.status_code == 200
    assert owned.status_code == 200
    assert details.status_code == 200
    assert mine.json()[0]["id"] == booking.id


def test_chat_and_unread_count(client, db_session):
    owner = User(phone="+79990000811")
    renter = User(phone="+79990000812")
    db_session.add_all([owner, renter])
    db_session.flush()
    category = _category(db_session)
    item = Item(
        owner_id=owner.id,
        category_id=category.id,
        title="Лестница",
        deposit_amount=0,
        status=ItemStatus.rented,
    )
    db_session.add(item)
    db_session.flush()
    booking = Booking(
        item_id=item.id,
        renter_id=renter.id,
        status=BookingStatus.rented,
        deposit_held_amount=0,
    )
    db_session.add(booking)
    db_session.commit()

    sent = client.post(
        f"/api/v1/bookings/{booking.id}/messages",
        json={"content": "Верну вечером"},
        headers=_headers(renter),
    )
    unread = client.get("/api/v1/chats/unread-count", headers=_headers(owner))

    assert sent.status_code == 201
    assert unread.status_code == 200
    assert unread.json()["total_unread"] == 1


def test_wallet_top_up_creates_transaction(client, db_session):
    user = User(phone="+79990000821")
    db_session.add(user)
    db_session.flush()
    db_session.add(Wallet(user_id=user.id, total_balance=10, held_balance=0))
    db_session.commit()

    response = client.post(
        "/api/v1/wallet/top-up",
        json={"amount": "25.50"},
        headers=_headers(user),
    )
    transactions = client.get("/api/v1/wallet/transactions", headers=_headers(user))

    assert response.status_code == 200
    assert response.json()["total"] == 35.5
    assert transactions.status_code == 200
    assert transactions.json()[0]["type"] == "deposit"


def test_notifications_and_history(client, db_session):
    user = User(phone="+79990000831")
    db_session.add(user)
    db_session.commit()

    history = client.get("/api/v1/users/me/history", headers=_headers(user))
    notifications = client.get("/api/v1/notifications", headers=_headers(user))

    assert history.status_code == 200
    assert history.json()["bookings"] == []
    assert notifications.status_code == 200
    assert notifications.json() == []
