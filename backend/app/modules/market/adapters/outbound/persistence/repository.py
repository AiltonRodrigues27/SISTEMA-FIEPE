from dataclasses import replace

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.modules.market.adapters.outbound.persistence.models import TransactionModel
from app.modules.market.domain.transaction import Transaction, TransactionType
from app.modules.market.ports.repositories import TransactionRepository


class SqlAlchemyTransactionRepository(TransactionRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, transaction: Transaction) -> Transaction:
        model = TransactionModel(
            club_id=transaction.club_id,
            player_id=transaction.player_id,
            player_name=transaction.player_name,
            type=transaction.type.value,
            value=transaction.value,
            fee=transaction.fee,
            penalty=transaction.penalty,
            profit=transaction.profit,
            cash_change=transaction.cash_change,
            created_at=transaction.created_at,
        )
        self._session.add(model)
        self._session.flush()
        return replace(transaction, id=model.id)

    def club_sold_player(self, club_id: int, player_id: int) -> bool:
        statement = select(
            exists().where(
                TransactionModel.club_id == club_id,
                TransactionModel.player_id == player_id,
                TransactionModel.type == TransactionType.VENDA.value,
            )
        )
        return bool(self._session.scalar(statement))
