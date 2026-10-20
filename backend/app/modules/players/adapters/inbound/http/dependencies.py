from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from app.modules.players.adapters.outbound.persistence.repository import (
    SqlAlchemyPlayerRepository,
)
from app.modules.players.application.change_player_condition import ChangePlayerCondition
from app.modules.players.application.create_player import CreatePlayer
from app.modules.players.application.delete_player import DeletePlayer
from app.modules.players.application.get_player import GetPlayer
from app.modules.players.application.update_player import UpdatePlayer


def build_create_player(session: Annotated[Session, Depends(get_db)]) -> CreatePlayer:
    return CreatePlayer(SqlAlchemyPlayerRepository(session), SqlAlchemyUnitOfWork(session))


def build_get_player(session: Annotated[Session, Depends(get_db)]) -> GetPlayer:
    return GetPlayer(SqlAlchemyPlayerRepository(session))


def build_update_player(session: Annotated[Session, Depends(get_db)]) -> UpdatePlayer:
    return UpdatePlayer(SqlAlchemyPlayerRepository(session), SqlAlchemyUnitOfWork(session))


def build_change_player_condition(
    session: Annotated[Session, Depends(get_db)],
) -> ChangePlayerCondition:
    return ChangePlayerCondition(SqlAlchemyPlayerRepository(session), SqlAlchemyUnitOfWork(session))


def build_delete_player(session: Annotated[Session, Depends(get_db)]) -> DeletePlayer:
    return DeletePlayer(SqlAlchemyPlayerRepository(session), SqlAlchemyUnitOfWork(session))
