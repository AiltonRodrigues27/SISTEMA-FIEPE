from collections.abc import Callable, Sequence
from decimal import Decimal

import pytest

from app.modules.clubs.application.public_operations import ClubAccount
from app.modules.clubs.domain.errors import ClubNotFound
from app.modules.players.application.public_operations import PlayerView
from app.modules.players.domain.entities import Attributes
from app.modules.players.domain.enums import PhysicalCondition, Position
from app.modules.players.domain.errors import PlayerNotFound
from app.modules.players.domain.listing import POSITION_ORDER


class InMemoryLineupRepository:
    def __init__(self) -> None:
        self.stored: dict[int, list[int]] = {}

    def list_player_ids(self, club_id: int) -> list[int]:
        return list(self.stored.get(club_id, []))

    def replace(self, club_id: int, player_ids: Sequence[int]) -> None:
        self.stored[club_id] = list(player_ids)

    def remove_player(self, player_id: int) -> None:
        for club_id, player_ids in self.stored.items():
            self.stored[club_id] = [item for item in player_ids if item != player_id]


class FakePlayersOperations:
    def __init__(self) -> None:
        self.views: dict[int, PlayerView] = {}

    def get_view(self, player_id: int) -> PlayerView:
        view = self.views.get(player_id)
        if view is None:
            raise PlayerNotFound("Jogador não encontrado.")
        return view

    def list_by_club(self, club_id: int) -> list[PlayerView]:
        squad = [view for view in self.views.values() if view.club_id == club_id]
        return sorted(squad, key=lambda view: (POSITION_ORDER[view.position], view.name, view.id))


class FakeClubsOperations:
    def __init__(self) -> None:
        self.formations: dict[int, str | None] = {}

    def get_account(self, club_id: int) -> ClubAccount:
        self._ensure_exists(club_id)
        return ClubAccount(club_id=club_id, cash=Decimal("300.00"))

    def get_formation(self, club_id: int) -> str | None:
        self._ensure_exists(club_id)
        return self.formations[club_id]

    def set_formation(self, club_id: int, formation: str) -> None:
        self._ensure_exists(club_id)
        self.formations[club_id] = formation

    def _ensure_exists(self, club_id: int) -> None:
        if club_id not in self.formations:
            raise ClubNotFound("Clube não encontrado.")


class FakeUnitOfWork:
    def __init__(self) -> None:
        self.commits = 0

    def commit(self) -> None:
        self.commits += 1


@pytest.fixture
def lineups() -> InMemoryLineupRepository:
    return InMemoryLineupRepository()


@pytest.fixture
def players_operations() -> FakePlayersOperations:
    return FakePlayersOperations()


@pytest.fixture
def clubs_operations() -> FakeClubsOperations:
    operations = FakeClubsOperations()
    operations.formations[1] = None
    return operations


@pytest.fixture
def unit_of_work() -> FakeUnitOfWork:
    return FakeUnitOfWork()


@pytest.fixture
def add_player(players_operations: FakePlayersOperations) -> Callable[..., PlayerView]:
    def add(
        player_id: int,
        name: str,
        position: Position,
        club_id: int | None = 1,
        condition: PhysicalCondition = PhysicalCondition.APTO,
    ) -> PlayerView:
        view = PlayerView(
            id=player_id,
            name=name,
            position=position,
            agility=85,
            age=25,
            condition=condition,
            base_value=Decimal("40.00"),
            market_value=Decimal("40.00"),
            attributes=Attributes(70, 68, 82, 79, 55, 64),
            potential=86,
            overall=75,
            club_id=club_id,
        )
        players_operations.views[player_id] = view
        return view

    return add


@pytest.fixture
def squad(add_player: Callable[..., PlayerView]) -> list[PlayerView]:
    return [
        add_player(30, "Rui Prado", Position.GOL),
        add_player(31, "Davi Lins", Position.LAT),
        add_player(32, "Teo Brandao", Position.ZAG),
        add_player(33, "Lauro Neves", Position.MEI),
        add_player(34, "Otto Rangel", Position.ATA),
        add_player(35, "Caio Dias", Position.ATA),
    ]
