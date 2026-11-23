"""Use cases for in-app notifications."""


class NotificationService:
    def __init__(self, *, uow, notifications):
        self.uow = uow
        self.notifications = notifications

    def list_notifications(self, user_id: int, cursor: str | None, limit: int):
        return self.notifications.list_by_user(user_id, cursor, limit)

    def mark_read(self, user_id: int, ids: list[int] | None, all_: bool) -> int:
        count = self.notifications.mark_read(user_id, ids, all_)
        self.uow.commit()
        return count
