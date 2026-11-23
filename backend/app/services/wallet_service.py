"""Use cases for virtual wallet."""

from decimal import Decimal

from app.domain.enums import TransactionType


class WalletService:
    def __init__(self, *, uow, wallets, transactions):
        self.uow = uow
        self.wallets = wallets
        self.transactions = transactions

    def get_wallet(self, user_id: int):
        wallet = self.wallets.get_by_user(user_id)
        if wallet is None:
            return {"total": Decimal("0"), "held": Decimal("0"), "available": Decimal("0")}
        return {
            "total": wallet.total_balance,
            "held": wallet.held_balance,
            "available": Decimal(str(wallet.total_balance)) - Decimal(str(wallet.held_balance)),
        }

    def top_up(self, user_id: int, amount: Decimal):
        wallet = self.wallets.get_by_user(user_id)
        if wallet is None:
            wallet = self.wallets.add(dict(user_id=user_id, total_balance=0, held_balance=0))
        wallet.total_balance = Decimal(str(wallet.total_balance)) + amount
        self.transactions.add(
            dict(user_id=user_id, booking_id=None, type=TransactionType.deposit, amount=amount)
        )
        self.uow.commit()
        return self.get_wallet(user_id)

    def list_transactions(
        self,
        user_id: int,
        type_: str | None,
        cursor: str | None,
        limit: int,
    ):
        return self.transactions.list_by_user(user_id, type_, cursor, limit)
