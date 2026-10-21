import pytest

from app.modules.players.application.public_operations import PlayersPublicOperations
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

    def list_active(self) -> list[Player]:
        return list(self.stored.values())

    def list_by_club(self, club_id: int) -> list[Player]:
        return [player for player in self.stored.values() if player.club_id == club_id]

    def list_in_clubs(self) -> list[Player]:
        return [player for player in self.stored.values() if player.club_id is not None]

    def update(self, player: Player) -> None:
        self.stored[player.id] = player

    def mark_deleted(self, player_id: int) -> None:
        del self.stored[player_id]


class FakeUnitOfWork:
    def __init__(self) -> None:
        self.commits = 0

    def commit(self) -> None:
        self.commits += 1


class FakeClubLookup:
    def __init__(self, existing_ids: set[int]) -> None:
        self._existing_ids = existing_ids

    def exists(self, club_id: int) -> bool:
        return club_id in self._existing_ids


class FakeLineupGateway:
    def __init__(self) -> None:
        self.removed: list[int] = []

    def remove_player(self, player_id: int) -> None:
        self.removed.append(player_id)


@pytest.fixture
def player_repository() -> InMemoryPlayerRepository:
    return InMemoryPlayerRepository()


@pytest.fixture
def lineup_gateway() -> FakeLineupGateway:
    return FakeLineupGateway()


@pytest.fixture
def operations(
    player_repository: InMemoryPlayerRepository, lineup_gateway: FakeLineupGateway
) -> PlayersPublicOperations:
    return PlayersPublicOperations(player_repository, lineup_gateway)


@pytest.fixture
def unit_of_work() -> FakeUnitOfWork:
    return FakeUnitOfWork()


@pytest.fixture
def club_lookup() -> FakeClubLookup:
    return FakeClubLookup(existing_ids={1, 2, 3})


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


@pytest.fixture
def saved_player(player_repository: InMemoryPlayerRepository, registration) -> Player:
    return player_repository.add(Player.register(registration))
