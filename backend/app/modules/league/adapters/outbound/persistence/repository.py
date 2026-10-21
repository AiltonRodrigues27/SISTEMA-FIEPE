from collections.abc import Sequence

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.modules.league.adapters.outbound.persistence.models import LineupModel
from app.modules.league.ports.repositories import LineupRepository

# "fetch" tira da sessão os objetos apagados, para o replace poder reinserir o mesmo jogador.
SYNC_DELETED_ROWS = {"synchronize_session": "fetch"}


class SqlAlchemyLineupRepository(LineupRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_player_ids(self, club_id: int) -> list[int]:
        statement = select(LineupModel.player_id).where(LineupModel.club_id == club_id)
        return list(self._session.scalars(statement))

    def replace(self, club_id: int, player_ids: Sequence[int]) -> None:
        statement = delete(LineupModel).where(LineupModel.club_id == club_id)
        self._session.execute(statement.execution_options(**SYNC_DELETED_ROWS))
        self._session.add_all(
            LineupModel(club_id=club_id, player_id=player_id) for player_id in player_ids
        )
        self._session.flush()

    def remove_player(self, player_id: int) -> None:
        statement = delete(LineupModel).where(LineupModel.player_id == player_id)
        self._session.execute(statement.execution_options(**SYNC_DELETED_ROWS))
