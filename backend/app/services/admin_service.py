"""Use cases for moderator administration."""


class AdminService:
    def __init__(self, *, uow, disputes):
        self.uow = uow
        self.disputes = disputes

    def list_disputes(self, status: str):
        return self.disputes.list_by_status(status)
