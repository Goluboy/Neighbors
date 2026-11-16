"""pytest fixtures: in-memory SQLite вместо PostgreSQL для тестов."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.composition.container import get_code_storage
from app.core.database import Base, get_db
from app.infrastructure.sms import InMemoryCodeStorage
from app.main import app
from app.persistence import models  # noqa: F401 — регистрация таблиц в metadata


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine)()
    engine.dispose()


@pytest.fixture()
def client(db_session):
    code_storage = InMemoryCodeStorage()
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_code_storage] = lambda: code_storage
    yield TestClient(app)
    app.dependency_overrides.clear()
