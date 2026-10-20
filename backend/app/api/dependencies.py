from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.infrastructure.clock import SystemClock
from app.infrastructure.database import get_db
from app.modules.clubs.adapters.outbound.persistence.contract_repository import (
    SqlAlchemyContractRepository,
)
from app.modules.clubs.adapters.outbound.persistence.repository import SqlAlchemyClubRepository
from app.modules.clubs.application.get_club import GetClub
from app.modules.clubs.application.list_clubs import ListClubs
from app.modules.clubs.application.public_operations import ClubsPublicOperations
from app.modules.players.adapters.outbound.persistence.repository import (
    SqlAlchemyPlayerRepository,
)
from app.modules.players.application.list_players import ListPlayers
from app.modules.players.application.public_operations import PlayersPublicOperations
from app.shared.domain.errors import NotFoundError

MAX_RESOURCE_ID = 2_147_483_647


def parse_resource_id(raw_id: str) -> int:
    if not (raw_id.isascii() and raw_id.isdigit()) or raw_id.startswith("0"):
        raise NotFoundError("Recurso não encontrado.")
    resource_id = int(raw_id)
    if resource_id > MAX_RESOURCE_ID:
        raise NotFoundError("Recurso não encontrado.")
    return resource_id


def build_list_players(session: Annotated[Session, Depends(get_db)]) -> ListPlayers:
    clubs = ClubsPublicOperations(SqlAlchemyClubRepository(session))
    return ListPlayers(SqlAlchemyPlayerRepository(session), clubs)


def build_list_clubs(session: Annotated[Session, Depends(get_db)]) -> ListClubs:
    players = PlayersPublicOperations(SqlAlchemyPlayerRepository(session))
    return ListClubs(SqlAlchemyClubRepository(session), players)


def build_get_club(session: Annotated[Session, Depends(get_db)]) -> GetClub:
    players = PlayersPublicOperations(SqlAlchemyPlayerRepository(session))
    return GetClub(
        SqlAlchemyClubRepository(session),
        SqlAlchemyContractRepository(session),
        players,
        SystemClock(),
    )
