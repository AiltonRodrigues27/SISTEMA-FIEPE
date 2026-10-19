import pytest

from app.modules.players.domain.entities import Attributes, Player, PlayerRegistration
from app.modules.players.domain.enums import Position


class InMemoryPlayerRepository:
    def __init__(self) -> None:
        self.stored: dict[int, Player] = {}
        self._next_id = 1

    def add(self, player: Player) -> Player:
        player.id = self._next_id
        self.stored[player.id] = player
        self._next_id += 1
        return player

    def get(self, player_id: int) -> Player | None:
        return self.stored.get(player_id)


class FakeUnitOfWork:
    def __init__(self) -> None:
        self.commits = 0

    def commit(self) -> None:
        self.commits += 1


@pytest.fixture
def player_repository() -> InMemoryPlayerRepository:
    return InMemoryPlayerRepository()


@pytest.fixture
def unit_of_work() -> FakeUnitOfWork:
    return FakeUnitOfWork()


@pytest.fixture
def registration() -> PlayerRegistration:
    return PlayerRegistration(
        name="Vini Jr",
        position=Position.MEI,
        agility=85,
        age=25,
        attributes=Attributes(70, 68, 82, 79, 55, 64),
        potential=86,
    )
