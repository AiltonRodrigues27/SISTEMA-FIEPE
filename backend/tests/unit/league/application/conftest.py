from collections.abc import Callable, Sequence
from dataclasses import replace
from datetime import datetime
from decimal import Decimal

import pytest

from app.modules.clubs.application.public_operations import ClubAccount
from app.modules.clubs.domain.errors import ClubNotFound
from app.modules.league.domain.match import Match
from app.modules.players.application.public_operations import PlayerView
from app.modules.players.domain.entities import Attributes
from app.modules.players.domain.enums import PhysicalCondition, Position
from app.modules.players.domain.errors import PlayerNotFound
from app.modules.players.domain.listing import POSITION_ORDER
from app.shared.domain.brasilia_time import BRASILIA

DEFAULT_ATTRIBUTES = Attributes(70, 68, 82, 79, 55, 64)


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


class InMemoryMatchRepository:
    def __init__(self) -> None:
        self.stored: list[Match] = []

    def add(self, match: Match) -> Match:
        saved = replace(match, id=len(self.stored) + 1)
        self.stored.append(saved)
        return saved

    def get(self, match_id: int) -> Match | None:
        return next((match for match in self.stored if match.id == match_id), None)

    def list_matches(self, club_id: int | None) -> list[Match]:
        found = [
            replace(match, duels=())
            for match in self.stored
            if club_id is None or club_id in (match.home_club_id, match.away_club_id)
        ]
        return sorted(found, key=lambda match: (match.played_at, match.id), reverse=True)


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
        self.names: dict[int, str] = {}

    def add_club(self, club_id: int, name: str) -> None:
        self.formations[club_id] = None
        self.names[club_id] = name

    def get_account(self, club_id: int) -> ClubAccount:
        self._ensure_exists(club_id)
        return ClubAccount(club_id=club_id, cash=Decimal("300.00"))

    def get_formation(self, club_id: int) -> str | None:
        self._ensure_exists(club_id)
        return self.formations[club_id]

    def set_formation(self, club_id: int, formation: str) -> None:
        self._ensure_exists(club_id)
        self.formations[club_id] = formation

    def list_club_names(self) -> dict[int, str]:
        return {club_id: self.names.get(club_id, f"Clube {club_id}") for club_id in self.formations}

    def _ensure_exists(self, club_id: int) -> None:
        if club_id not in self.formations:
            raise ClubNotFound("Clube não encontrado.")


class FakeUnitOfWork:
    def __init__(self) -> None:
        self.commits = 0

    def commit(self) -> None:
        self.commits += 1


class FixedClock:
    def __init__(self, moment: datetime) -> None:
        self.moment = moment

    def now(self) -> datetime:
        return self.moment


@pytest.fixture
def lineups() -> InMemoryLineupRepository:
    return InMemoryLineupRepository()


@pytest.fixture
def matches() -> InMemoryMatchRepository:
    return InMemoryMatchRepository()


@pytest.fixture
def players_operations() -> FakePlayersOperations:
    return FakePlayersOperations()


@pytest.fixture
def clubs_operations() -> FakeClubsOperations:
    operations = FakeClubsOperations()
    operations.add_club(1, "Águias FC")
    return operations


@pytest.fixture
def unit_of_work() -> FakeUnitOfWork:
    return FakeUnitOfWork()


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock(datetime(2026, 11, 12, 15, 0, tzinfo=BRASILIA))


@pytest.fixture
def add_player(players_operations: FakePlayersOperations) -> Callable[..., PlayerView]:
    def add(
        player_id: int,
        name: str,
        position: Position,
        club_id: int | None = 1,
        condition: PhysicalCondition = PhysicalCondition.APTO,
        attributes: Attributes = DEFAULT_ATTRIBUTES,
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
            attributes=attributes,
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


@pytest.fixture
def give_lineup(
    add_player: Callable[..., PlayerView],
    lineups: InMemoryLineupRepository,
    clubs_operations: FakeClubsOperations,
) -> Callable[..., list[PlayerView]]:
    """Cria o clube com os 5 titulares gravados na escalação e a formação salva."""

    def give(
        club_id: int, name: str, formation: str, starters: Sequence[tuple]
    ) -> list[PlayerView]:
        clubs_operations.add_club(club_id, name)
        views = [
            add_player(player_id, player_name, position, club_id, condition, attributes)
            for player_id, player_name, position, condition, attributes in starters
        ]
        lineups.replace(club_id, [view.id for view in views])
        clubs_operations.set_formation(club_id, formation)
        return views

    return give
