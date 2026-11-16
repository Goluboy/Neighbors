"""Идентичность аутентифицированного пользователя для прикладного слоя."""

from dataclasses import dataclass

from app.domain.enums import UserRole, UserStatus


@dataclass(frozen=True)
class CurrentUser:
    id: int
    role: UserRole
    status: UserStatus
    latitude: float | None = None
    longitude: float | None = None
