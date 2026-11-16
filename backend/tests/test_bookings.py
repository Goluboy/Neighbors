"""UC-3: заявка атомарно холдирует залог; нехватка средств отменяет заявку."""

from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.security import create_access_token
from app.domain.enums import ItemStatus
from app.persistence.models import Booking, Category, Item, User, Wallet, WalletTransaction


def _make_user(db, phone: str, balance: str | None = None) -> User:
    user = User(phone=phone)
    db.add(user)
    db.flush()
    if balance is not None:
        db.add(Wallet(user_id=user.id, total_balance=balance, held_balance=0))
    db.commit()
    return user


def _make_item(db, owner: User, deposit: str) -> Item:
    category = db.scalar(select(Category).where(Category.slug == "repair"))
    if category is None:
        category = Category(name="Ремонт", slug="repair")
        db.add(category)
        db.flush()
    item = Item(
        owner_id=owner.id,
        category_id=category.id,
        title="Дрель",
        deposit_amount=deposit,
        status=ItemStatus.available,
    )
    db.add(item)
    db.commit()
    return item


def _headers(user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token(user.id)}"}


def _booking_body(item_id: int) -> dict:
    now = datetime.now(timezone.utc)
    return {
        "item_id": item_id,
        "start_date": (now + timedelta(days=1)).isoformat(),
        "end_date": (now + timedelta(days=3)).isoformat(),
    }


def test_unknown_item_returns_domain_error(client, db_session):
    renter = _make_user(db_session, "+79990000001", balance="0")

    response = client.post(
        "/api/v1/bookings", json=_booking_body(999_999), headers=_headers(renter)
    )

    assert response.status_code == 404, response.text
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_booking_without_funds_leaves_item_available(client, db_session):
    owner = _make_user(db_session, "+79990000002")
    renter = _make_user(db_session, "+79990000003", balance="10")
    item = _make_item(db_session, owner, deposit="100")

    response = client.post(
        "/api/v1/bookings", json=_booking_body(item.id), headers=_headers(renter)
    )

    assert response.status_code == 400, response.text
    assert response.json()["error"]["code"] == "INSUFFICIENT_FUNDS"
    db_session.expire_all()
    assert db_session.get(Item, item.id).status == ItemStatus.available
    assert db_session.scalar(select(Booking).where(Booking.item_id == item.id)) is None


def test_booking_holds_deposit_and_marks_item_booked(client, db_session):
    owner = _make_user(db_session, "+79990000004")
    renter = _make_user(db_session, "+79990000005", balance="500")
    item = _make_item(db_session, owner, deposit="100")

    response = client.post(
        "/api/v1/bookings", json=_booking_body(item.id), headers=_headers(renter)
    )

    assert response.status_code == 201, response.text
    assert float(response.json()["deposit_held_amount"]) == 100.0

    db_session.expire_all()
    wallet = db_session.scalar(select(Wallet).where(Wallet.user_id == renter.id))
    assert float(wallet.total_balance) == 400.0
    assert float(wallet.held_balance) == 100.0
    assert db_session.get(Item, item.id).status == ItemStatus.booked
    hold = db_session.scalar(
        select(WalletTransaction).where(WalletTransaction.user_id == renter.id)
    )
    assert hold is not None
    assert hold.type.value == "hold"
