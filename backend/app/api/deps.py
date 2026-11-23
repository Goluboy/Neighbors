"""FastAPI-зависимости: UnitOfWork, сервисы, текущий пользователь, роли."""

from collections.abc import Iterator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.composition.container import (
    get_code_factory,
    get_code_storage,
    get_event_bus,
    get_sms_sender,
)
from app.core.database import get_db
from app.core.security import decode_token
from app.domain.enums import UserRole, UserStatus
from app.domain.identity import CurrentUser
from app.persistence.unit_of_work import SqlAlchemyUnitOfWork
from app.services.admin_service import AdminService
from app.services.auth_service import AuthService
from app.services.booking_service import BookingService
from app.services.catalog_service import CatalogService
from app.services.category_service import CategoryService
from app.services.chat_service import ChatService
from app.services.item_service import ItemService
from app.services.notification_service import NotificationService
from app.services.profile_service import ProfileService
from app.services.wallet_service import WalletService

security = HTTPBearer()


def get_uow(db: Session = Depends(get_db)) -> Iterator[SqlAlchemyUnitOfWork]:
    uow = SqlAlchemyUnitOfWork(db)
    try:
        yield uow
    except Exception:
        uow.rollback()
        raise


def get_auth_service(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
    sms=Depends(get_sms_sender),
    codes=Depends(get_code_storage),
    new_code=Depends(get_code_factory),
) -> AuthService:
    return AuthService(
        uow=uow, users=uow.users, wallets=uow.wallets, sms=sms, codes=codes, new_code=new_code
    )


def get_profile_service(uow: SqlAlchemyUnitOfWork = Depends(get_uow)) -> ProfileService:
    return ProfileService(
        uow=uow,
        users=uow.users,
        wallets=uow.wallets,
        reviews=uow.reviews,
        bookings=uow.bookings,
        transactions=uow.transactions,
    )


def get_item_service(uow: SqlAlchemyUnitOfWork = Depends(get_uow)) -> ItemService:
    return ItemService(uow=uow, items=uow.items, bookings=uow.bookings, categories=uow.categories)


def get_catalog_service(uow: SqlAlchemyUnitOfWork = Depends(get_uow)) -> CatalogService:
    return CatalogService(items=uow.items)


def get_category_service(uow: SqlAlchemyUnitOfWork = Depends(get_uow)) -> CategoryService:
    return CategoryService(categories=uow.categories)


def get_booking_service(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
    event_bus=Depends(get_event_bus),
) -> BookingService:
    return BookingService(
        uow=uow,
        bookings=uow.bookings,
        items=uow.items,
        wallets=uow.wallets,
        notifications=uow.notifications,
        event_bus=event_bus,
    )


def get_chat_service(uow: SqlAlchemyUnitOfWork = Depends(get_uow)) -> ChatService:
    return ChatService(uow=uow, bookings=uow.bookings, messages=uow.messages)


def get_wallet_service(uow: SqlAlchemyUnitOfWork = Depends(get_uow)) -> WalletService:
    return WalletService(
        uow=uow,
        wallets=uow.wallets,
        transactions=uow.transactions,
    )


def get_notification_service(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> NotificationService:
    return NotificationService(uow=uow, notifications=uow.notifications)


def get_admin_service(uow: SqlAlchemyUnitOfWork = Depends(get_uow)) -> AdminService:
    return AdminService(uow=uow, disputes=uow.disputes)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> CurrentUser:
    try:
        payload = decode_token(credentials.credentials)
    except ValueError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    if payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Wrong token type")

    record = uow.users.get(int(payload["sub"]))
    if record is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if record.status == UserStatus.blocked:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Account is blocked")
    return CurrentUser(
        id=record.id,
        role=record.role,
        status=record.status,
        latitude=float(record.latitude) if record.latitude is not None else None,
        longitude=float(record.longitude) if record.longitude is not None else None,
    )


def require_moderator(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if user.role != UserRole.moderator:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Moderator role required")
    return user
