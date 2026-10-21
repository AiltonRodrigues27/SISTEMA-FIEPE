from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.infrastructure.clock import SystemClock
from app.infrastructure.database import get_db
from app.infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from app.modules.clubs.adapters.outbound.persistence.contract_repository import (
    SqlAlchemyContractRepository,
)
from app.modules.clubs.adapters.outbound.persistence.repository import SqlAlchemyClubRepository
from app.modules.clubs.application.get_club import GetClub
from app.modules.clubs.application.list_clubs import ListClubs
from app.modules.clubs.application.public_operations import ClubsPublicOperations
from app.modules.market.adapters.outbound.persistence.repository import (
    SqlAlchemyTransactionRepository,
)
from app.modules.market.application.buy_player import BuyPlayer
from app.modules.market.application.list_transactions import ListTransactions
from app.modules.market.application.sell_player import SellPlayer
from app.modules.players.adapters.outbound.persistence.repository import (
    SqlAlchemyPlayerRepository,
)
from app.modules.players.application.list_players import ListPlayers
from app.modules.players.application.public_operations import PlayersPublicOperations
from app.shared.application.clock import Clock
from app.shared.domain.errors import NotFoundError

MAX_RESOURCE_ID = 2_147_483_647


def parse_resource_id(raw_id: str) -> int:
    if not (raw_id.isascii() and raw_id.isdigit()) or raw_id.startswith("0"):
        raise NotFoundError("Recurso não encontrado.")
    resource_id = int(raw_id)
    if resource_id > MAX_RESOURCE_ID:
        raise NotFoundError("Recurso não encontrado.")
    return resource_id


def get_clock() -> Clock:
    return SystemClock()


def _players_operations(session: Session) -> PlayersPublicOperations:
    return PlayersPublicOperations(SqlAlchemyPlayerRepository(session))


def _clubs_operations(session: Session) -> ClubsPublicOperations:
    return ClubsPublicOperations(
        SqlAlchemyClubRepository(session),
        SqlAlchemyContractRepository(session),
        _players_operations(session),
    )


def build_list_players(session: Annotated[Session, Depends(get_db)]) -> ListPlayers:
    return ListPlayers(SqlAlchemyPlayerRepository(session), _clubs_operations(session))


def build_list_clubs(session: Annotated[Session, Depends(get_db)]) -> ListClubs:
    return ListClubs(SqlAlchemyClubRepository(session), _players_operations(session))


def build_get_club(
    session: Annotated[Session, Depends(get_db)], clock: Annotated[Clock, Depends(get_clock)]
) -> GetClub:
    return GetClub(
        SqlAlchemyClubRepository(session),
        SqlAlchemyContractRepository(session),
        _players_operations(session),
        clock,
    )


def build_buy_player(
    session: Annotated[Session, Depends(get_db)], clock: Annotated[Clock, Depends(get_clock)]
) -> BuyPlayer:
    return BuyPlayer(
        _players_operations(session),
        _clubs_operations(session),
        SqlAlchemyTransactionRepository(session),
        clock,
        SqlAlchemyUnitOfWork(session),
    )


def build_list_transactions(session: Annotated[Session, Depends(get_db)]) -> ListTransactions:
    return ListTransactions(
        _players_operations(session),
        _clubs_operations(session),
        SqlAlchemyTransactionRepository(session),
    )


def build_sell_player(
    session: Annotated[Session, Depends(get_db)], clock: Annotated[Clock, Depends(get_clock)]
) -> SellPlayer:
    return SellPlayer(
        _players_operations(session),
        _clubs_operations(session),
        SqlAlchemyTransactionRepository(session),
        clock,
        SqlAlchemyUnitOfWork(session),
    )
