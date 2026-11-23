"""Use cases for chat within a booking."""

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.domain.enums import BookingStatus


class ChatService:
    def __init__(self, *, uow, bookings, messages):
        self.uow = uow
        self.bookings = bookings
        self.messages = messages

    def _get_participant_booking(self, booking_id: int, user_id: int):
        booking = self.bookings.get(booking_id)
        if booking is None:
            raise NotFoundError("Бронь не найдена")
        if booking.renter_id != user_id and booking.item.owner_id != user_id:
            raise PermissionDeniedError("Чат доступен только участникам брони")
        return booking

    def list_messages(self, booking_id: int, user_id: int, cursor: str | None, limit: int):
        self._get_participant_booking(booking_id, user_id)
        return self.messages.list_by_booking(booking_id, cursor, limit)

    def send_message(self, booking_id: int, user_id: int, content: str):
        booking = self._get_participant_booking(booking_id, user_id)
        if booking.status not in (BookingStatus.approved, BookingStatus.rented):
            raise PermissionDeniedError("Сообщения доступны после одобрения заявки")
        message = self.messages.add(dict(booking_id=booking_id, sender_id=user_id, content=content))
        self.uow.commit()
        return message

    def mark_read(self, booking_id: int, user_id: int, until_message_id: int) -> int:
        self._get_participant_booking(booking_id, user_id)
        count = self.messages.mark_read_until(booking_id, user_id, until_message_id)
        self.uow.commit()
        return count

    def unread_count(self, user_id: int) -> int:
        return self.messages.unread_count(user_id)
