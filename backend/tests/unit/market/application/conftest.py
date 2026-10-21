from collections.abc import Callable
from dataclasses import replace
from datetime import datetime
from decimal import Decimal

import pytest

from app.modules.clubs.application.public_operations import (
    ClubAccount,
    ContractTermination,
    PlayerSigning,
    SignedContract,
)
from app.modules.clubs.domain.errors import ClubNotFound
from app.modules.market.domain.transaction import Transaction
from app.modules.players.application.public_operations import PlayerView
from app.modules.players.domain.entities import Attributes
from app.modules.players.domain.enums import PhysicalCondition, Position
from app.modules.players.domain.errors import PlayerIsFree, PlayerNotFound, PlayerNotFree
from app.shared.domain.brasilia_time import BRASILIA


class FakePlayersOperations:
    def __init__(self) -> None:
        self.views: dict[int, PlayerView] = {}
        self.assigned: list[tuple[int, int]] = []
        self.released: list[int] = []

    def get_free_player(self, player_id: int) -> PlayerView:
        view = self._get(player_id)
        if view.club_id is not None:
            raise PlayerNotFree("O jogador já tem clube.")
        return view

    def get_player_with_club(self, player_id: int) -> PlayerView:
        view = self._get(player_id)
        if view.club_id is None:
            raise PlayerIsFree("Jogador livre não pode ser vendido.")
        return view

    def assign_to_club(self, player_id: int, club_id: int) -> None:
        self.assigned.append((player_id, club_id))

    def release_from_club(self, player_id: int) -> int:
        self.released.append(player_id)
        return self.views[player_id].club_id

    def _get(self, player_id: int) -> PlayerView:
        view = self.views.get(player_id)
        if view is None:
            raise PlayerNotFound("Jogador não encontrado.")
        return view


class FakeClubsOperations:
    def __init__(self) -> None:
        self.accounts: dict[int, ClubAccount] = {}
        self.signed: list[PlayerSigning] = []
        self.sign_error: Exception | None = None
        self.termination: ContractTermination | None = None
        self.termination_error: Exception | None = None
        self.terminated: list[int] = []
        self.credits: list[tuple[int, Decimal]] = []

    def get_account(self, club_id: int) -> ClubAccount:
        account = self.accounts.get(club_id)
        if account is None:
            raise ClubNotFound("Clube não encontrado.")
        return account

    def sign_player(self, signing: PlayerSigning, now: datetime) -> SignedContract:
        if self.sign_error is not None:
            raise self.sign_error
        self.signed.append(signing)
        return SignedContract(signing.purchase_value, signing.loyalty_until, "ATIVO")

    def terminate_contract(
        self, player_id: int, market_value: Decimal, now: datetime
    ) -> ContractTermination:
        if self.termination_error is not None:
            raise self.termination_error
        self.terminated.append(player_id)
        return self.termination

    def credit_cash(self, club_id: int, amount: Decimal) -> Decimal:
        self.credits.append((club_id, amount))
        return self.accounts[club_id].cash + amount


class InMemoryTransactionRepository:
    def __init__(self) -> None:
        self.added: list[Transaction] = []
        self.sold: set[tuple[int, int]] = set()

    def add(self, transaction: Transaction) -> Transaction:
        saved = replace(transaction, id=len(self.added) + 1)
        self.added.append(saved)
        return saved

    def club_sold_player(self, club_id: int, player_id: int) -> bool:
        return (club_id, player_id) in self.sold


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
def players_operations() -> FakePlayersOperations:
    return FakePlayersOperations()


@pytest.fixture
def clubs_operations() -> FakeClubsOperations:
    return FakeClubsOperations()


@pytest.fixture
def transactions() -> InMemoryTransactionRepository:
    return InMemoryTransactionRepository()


@pytest.fixture
def unit_of_work() -> FakeUnitOfWork:
    return FakeUnitOfWork()


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock(datetime(2026, 11, 2, 10, 15, tzinfo=BRASILIA))


@pytest.fixture
def make_view() -> Callable[..., PlayerView]:
    def make(
        player_id: int = 2,
        name: str = "Meia Lua",
        club_id: int | None = None,
        market_value: str = "37.00",
    ) -> PlayerView:
        return PlayerView(
            id=player_id,
            name=name,
            position=Position.MEI,
            agility=85,
            age=25,
            condition=PhysicalCondition.MAL_CONDICIONADO,
            base_value=Decimal("40.00"),
            market_value=Decimal(market_value),
            attributes=Attributes(70, 68, 82, 79, 55, 64),
            potential=86,
            overall=75,
            club_id=club_id,
        )

    return make
