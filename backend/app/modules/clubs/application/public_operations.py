from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from app.modules.clubs.domain.contract import (
    Contract,
    calculate_penalty,
    penalty_percent,
    remaining_days,
)
from app.modules.clubs.domain.entities import Club
from app.modules.clubs.domain.errors import ClubNotFound, ContractNotFound
from app.modules.clubs.ports.contracts import ContractRepository
from app.modules.clubs.ports.repositories import ClubRepository
from app.modules.players.application.public_operations import PlayersPublicOperations


@dataclass(frozen=True)
class ClubAccount:
    club_id: int
    cash: Decimal


@dataclass(frozen=True)
class PlayerSigning:
    club_id: int
    player_id: int
    purchase_value: Decimal
    total_cost: Decimal
    loyalty_until: datetime


@dataclass(frozen=True)
class SignedContract:
    purchase_value: Decimal
    loyalty_until: datetime
    status: str


@dataclass(frozen=True)
class ContractTermination:
    purchase_value: Decimal
    remaining_days: int
    penalty_percent: int
    penalty: Decimal
    status: str


class ClubsPublicOperations:
    def __init__(
        self,
        clubs: ClubRepository,
        contracts: ContractRepository,
        players: PlayersPublicOperations,
    ) -> None:
        self._clubs = clubs
        self._contracts = contracts
        self._players = players

    def exists(self, club_id: int) -> bool:
        return self._clubs.get(club_id) is not None

    def get_account(self, club_id: int) -> ClubAccount:
        club = self._get_club(club_id)
        return ClubAccount(club_id=club_id, cash=club.cash)

    def sign_player(self, signing: PlayerSigning, now: datetime) -> SignedContract:
        club = self._get_club(signing.club_id)
        club.ensure_squad_has_room(len(self._players.list_by_club(signing.club_id)))
        contract = Contract.open(
            player_id=signing.player_id,
            club_id=signing.club_id,
            purchase_value=signing.purchase_value,
            loyalty_until=signing.loyalty_until,
            now=now,
        )
        club.debit(signing.total_cost)
        self._clubs.update(club)
        saved_contract = self._contracts.add(contract)
        return SignedContract(
            purchase_value=saved_contract.purchase_value,
            loyalty_until=saved_contract.loyalty_until,
            status=saved_contract.status.value,
        )

    def terminate_contract(
        self, player_id: int, market_value: Decimal, now: datetime
    ) -> ContractTermination:
        contract = self._contracts.get_active_by_player(player_id)
        if contract is None:
            raise ContractNotFound("O jogador não tem contrato ativo.")
        days = remaining_days(contract.loyalty_until, now)
        penalty = calculate_penalty(market_value, days)
        closed_contract = contract.close(now, penalty)
        self._contracts.update(closed_contract)
        return ContractTermination(
            purchase_value=contract.purchase_value,
            remaining_days=days,
            penalty_percent=penalty_percent(days),
            penalty=penalty,
            status=closed_contract.status.value,
        )

    def credit_cash(self, club_id: int, amount: Decimal) -> Decimal:
        club = self._get_club(club_id)
        club.credit(amount)
        self._clubs.update(club)
        return club.cash

    def _get_club(self, club_id: int) -> Club:
        club = self._clubs.get(club_id)
        if club is None:
            raise ClubNotFound("Clube não encontrado.")
        return club
