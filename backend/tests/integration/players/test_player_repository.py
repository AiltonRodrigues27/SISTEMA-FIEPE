from sqlalchemy import func, update

from app.modules.players.adapters.outbound.persistence.models import PlayerModel
from app.modules.players.adapters.outbound.persistence.repository import (
    SqlAlchemyPlayerRepository,
)
from app.modules.players.domain.entities import Attributes, Player, PlayerRegistration
from app.modules.players.domain.enums import Position

REGISTRATION = PlayerRegistration(
    name="Vini Jr",
    position=Position.MEI,
    agility=85,
    age=25,
    attributes=Attributes(
        pace=70, shooting=68, passing=82, dribbling=79, defending=55, physical=64
    ),
    potential=86,
)


def test_add_assigns_id_and_get_returns_the_same_player(session):
    repository = SqlAlchemyPlayerRepository(session)

    saved = repository.add(Player.register(REGISTRATION))
    session.expire_all()

    assert saved.id is not None
    assert repository.get(saved.id) == saved


def test_get_returns_none_for_unknown_id(session):
    assert SqlAlchemyPlayerRepository(session).get(999_999) is None


def test_get_returns_none_for_deleted_player(session):
    repository = SqlAlchemyPlayerRepository(session)
    saved = repository.add(Player.register(REGISTRATION))

    session.execute(
        update(PlayerModel).where(PlayerModel.id == saved.id).values(deleted_at=func.now())
    )

    assert repository.get(saved.id) is None
