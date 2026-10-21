from collections.abc import Callable
from dataclasses import replace
from datetime import datetime
from decimal import Decimal

import pytest

from app.modules.clubs.domain.contract import Contract, ContractStatus
from app.modules.clubs.domain.entities import Club
from app.modules.players.application.public_operations import PlayerView
from app.modules.players.domain.entities import Attributes
from app.modules.players.domain.enums import PhysicalCondition, Position
from app.shared.domain.brasilia_time import BRASILIA


class InMemoryClubRepository:
    def __init__(self) -> None:
        self.stored: dict[int, Club] = {}
        self._next_id = 1

    def add(self, club: Club) -> Club:
        club.id = self._next_id
        self.stored[club.id] = club
        self._next_id += 1
        return club

    def get(self, club_id: int) -> Club | None:
        return self.stored.get(club_id)

    def update(self, club: Club) -> None:
        self.stored[club.id] = club

    def list_all(self) -> list[Club]:
        return list(self.stored.values())

    def count(self) -> int:
        return len(self.stored)

    def name_exists(self, name: str) -> bool:
        return any(club.name.lower() == name.lower() for club in self.stored.values())

    def acronym_exists(self, acronym: str) -> bool:
        return any(club.acronym == acronym for club in self.stored.values())


class InMemoryContractRepository:
    def __init__(self) -> None:
        self.stored: list[Contract] = []

    def add(self, contract: Contract) -> Contract:
        saved = replace(contract, id=len(self.stored) + 1)
        self.stored.append(saved)
        return saved

    def get_active_by_player(self, player_id: int) -> Contract | None:
        for contract in self.stored:
            if contract.player_id == player_id and contract.status is ContractStatus.ATIVO:
                return contract
        return None

    def update(self, contract: Contract) -> None:
        self.stored = [contract if stored.id == contract.id else stored for stored in self.stored]

    def list_active_by_club(self, club_id: int) -> list[Contract]:
        return [
            contract
            for contract in self.stored
            if contract.club_id == club_id and contract.status is ContractStatus.ATIVO
        ]


class FakePlayersOperations:
    def __init__(self) -> None:
        self.views: list[PlayerView] = []

    def list_by_club(self, club_id: int) -> list[PlayerView]:
        return [view for view in self.views if view.club_id == club_id]

    def list_in_clubs(self) -> list[PlayerView]:
        return [view for view in self.views if view.club_id is not None]


class FakeUnitOfWork:
    def __init__(self) -> None:
        self.commits = 0

    def commit(self) -> None:
        self.commits += 1


class FixedClock:
    def __init__(self, moment: datetime) -> None:
        self._moment = moment

    def now(self) -> datetime:
        return self._moment


@pytest.fixture
def club_repository() -> InMemoryClubRepository:
    return InMemoryClubRepository()


@pytest.fixture
def contract_repository() -> InMemoryContractRepository:
    return InMemoryContractRepository()


@pytest.fixture
def players_operations() -> FakePlayersOperations:
    return FakePlayersOperations()


@pytest.fixture
def unit_of_work() -> FakeUnitOfWork:
    return FakeUnitOfWork()


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock(datetime(2026, 11, 2, 10, 15, tzinfo=BRASILIA))


@pytest.fixture
def add_club(club_repository: InMemoryClubRepository) -> Callable[..., Club]:
    def add(name: str, acronym: str, cash: str = "300.00") -> Club:
        club = Club.register(name, acronym)
        club.cash = Decimal(cash)
        return club_repository.add(club)

    return add


@pytest.fixture
def make_view() -> Callable[..., PlayerView]:
    def make(
        player_id: int = 1,
        name: str = "Ana Lima",
        club_id: int | None = 1,
        market_value: str = "40.00",
        position: Position = Position.MEI,
    ) -> PlayerView:
        return PlayerView(
            id=player_id,
            name=name,
            position=position,
            agility=85,
            age=25,
            condition=PhysicalCondition.APTO,
            base_value=Decimal("40.00"),
            market_value=Decimal(market_value),
            attributes=Attributes(70, 68, 82, 79, 55, 64),
            potential=86,
            overall=75,
            club_id=club_id,
        )

    return make
