# Representa como os dados são armazenados e recuperados do banco de dados, incluindo consultas e operações de persistência.
from sqlalchemy import func, select
from sqlalchemy import update as sql_update
from sqlalchemy.orm import Session

from app.modules.players.adapters.outbound.persistence.models import PlayerModel
from app.modules.players.domain.entities import Attributes, Player
from app.modules.players.domain.enums import PhysicalCondition, Position
from app.modules.players.domain.errors import PlayerNotFound
from app.modules.players.ports.repositories import PlayerRepository


class SqlAlchemyPlayerRepository(PlayerRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, player: Player) -> Player:
        model = _to_model(player)
        self._session.add(model)
        self._session.flush()
        player.id = model.id
        return player

    def get(self, player_id: int) -> Player | None:
        statement = select(PlayerModel).where(
            PlayerModel.id == player_id, PlayerModel.deleted_at.is_(None)
        )
        model = self._session.scalars(statement).first()
        return _to_entity(model) if model is not None else None

    def update(self, player: Player) -> None:
        model = self._session.get(PlayerModel, player.id)
        if model is None:
            raise PlayerNotFound("Jogador não encontrado.")
        model.name = player.name
        model.position = player.position.value
        model.agility = player.agility
        model.age = player.age
        model.condition = player.condition.value
        model.club_id = player.club_id
        self._session.flush()

    def mark_deleted(self, player_id: int) -> None:
        statement = (
            sql_update(PlayerModel).where(PlayerModel.id == player_id).values(deleted_at=func.now())
        )
        self._session.execute(statement)


def _to_model(player: Player) -> PlayerModel:
    return PlayerModel(
        name=player.name,
        position=player.position.value,
        agility=player.agility,
        age=player.age,
        base_value=player.base_value,
        condition=player.condition.value,
        club_id=player.club_id,
        pace=player.attributes.pace,
        shooting=player.attributes.shooting,
        passing=player.attributes.passing,
        dribbling=player.attributes.dribbling,
        defending=player.attributes.defending,
        physical=player.attributes.physical,
        potential=player.potential,
    )


def _to_entity(model: PlayerModel) -> Player:
    return Player(
        id=model.id,
        name=model.name,
        position=Position(model.position),
        agility=model.agility,
        age=model.age,
        condition=PhysicalCondition(model.condition),
        club_id=model.club_id,
        base_value=model.base_value,
        attributes=Attributes(
            pace=model.pace,
            shooting=model.shooting,
            passing=model.passing,
            dribbling=model.dribbling,
            defending=model.defending,
            physical=model.physical,
        ),
        potential=model.potential,
    )
