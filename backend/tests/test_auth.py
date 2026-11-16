"""UC-1: вход по коду подтверждения создаёт пользователя и кошелёк."""

from sqlalchemy import select

from app.persistence.models import User, Wallet

PHONE = "+79991234567"


def test_verify_creates_user_and_wallet(client, db_session):
    assert client.post("/api/v1/auth/phone/send-code", json={"phone": PHONE}).status_code == 202

    response = client.post("/api/v1/auth/phone/verify", json={"phone": PHONE, "code": "1234"})

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["is_new_user"] is True

    user = db_session.scalar(select(User).where(User.phone == PHONE))
    assert user is not None
    assert db_session.scalar(select(Wallet).where(Wallet.user_id == user.id)) is not None

    me = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert me.status_code == 200, me.text
    assert me.json()["phone"] == PHONE


def test_second_login_reuses_account(client, db_session):
    db_session.add(User(phone=PHONE))
    db_session.commit()

    client.post("/api/v1/auth/phone/send-code", json={"phone": PHONE})
    response = client.post("/api/v1/auth/phone/verify", json={"phone": PHONE, "code": "1234"})

    assert response.status_code == 200, response.text
    assert response.json()["is_new_user"] is False


def test_wrong_code_is_domain_error(client):
    client.post("/api/v1/auth/phone/send-code", json={"phone": PHONE})

    response = client.post("/api/v1/auth/phone/verify", json={"phone": PHONE, "code": "0000"})

    assert response.status_code == 400, response.text
    assert response.json()["error"]["code"] == "INVALID_CODE"
