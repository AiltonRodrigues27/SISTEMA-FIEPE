from dataclasses import replace

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.modules.market.adapters.outbound.persistence.models import TransactionModel
from app.modules.market.domain.history import TransactionFilters
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

    def list_by_club(self, club_id: int, filters: TransactionFilters) -> list[Transaction]:
        statement = select(TransactionModel).where(TransactionModel.club_id == club_id)
        if filters.types is not None:
            types = [transaction_type.value for transaction_type in filters.types]
            statement = statement.where(TransactionModel.type.in_(types))
        if filters.player_id is not None:
            statement = statement.where(TransactionModel.player_id == filters.player_id)
        statement = statement.order_by(
            TransactionModel.created_at.desc(), TransactionModel.id.desc()
        )
        return [_to_entity(model) for model in self._session.scalars(statement)]


def _to_entity(model: TransactionModel) -> Transaction:
    return Transaction(
        id=model.id,
        club_id=model.club_id,
        player_id=model.player_id,
        player_name=model.player_name,
        type=TransactionType(model.type),
        value=model.value,
        fee=model.fee,
        penalty=model.penalty,
        profit=model.profit,
        cash_change=model.cash_change,
        created_at=model.created_at,
    )
