from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from app.modules.clubs.adapters.outbound.persistence.repository import SqlAlchemyClubRepository
from app.modules.clubs.application.create_club import CreateClub


def build_create_club(session: Annotated[Session, Depends(get_db)]) -> CreateClub:
    return CreateClub(SqlAlchemyClubRepository(session), SqlAlchemyUnitOfWork(session))
