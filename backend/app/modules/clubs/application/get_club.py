from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from app.modules.clubs.domain.contract import Contract, penalty_percent, remaining_days
from app.modules.clubs.domain.entities import ClubView
from app.modules.clubs.domain.errors import ClubNotFound
from app.modules.clubs.domain.listing import calculate_squad_value
from app.modules.clubs.ports.contracts import ContractRepository
from app.modules.clubs.ports.repositories import ClubRepository
from app.modules.players.application.public_operations import PlayersPublicOperations, PlayerView
from app.shared.application.clock import Clock


@dataclass(frozen=True)
class ContractView:
    purchase_value: Decimal
    loyalty_until: datetime
    remaining_days: int
    penalty_percent: int


@dataclass(frozen=True)
class SquadMember:
    player: PlayerView
    contract: ContractView | None


@dataclass(frozen=True)
class ClubDetails:
    view: ClubView
    squad: list[SquadMember]


class GetClub:
    def __init__(
        self,
        clubs: ClubRepository,
        contracts: ContractRepository,
        players: PlayersPublicOperations,
        clock: Clock,
    ) -> None:
        self._clubs = clubs
        self._contracts = contracts
        self._players = players
        self._clock = clock

    def execute(self, club_id: int) -> ClubDetails:
        club = self._clubs.get(club_id)
        if club is None:
            raise ClubNotFound("Clube não encontrado.")
        players = self._players.list_by_club(club_id)
        contracts = {
            contract.player_id: contract
            for contract in self._contracts.list_active_by_club(club_id)
        }
        now = self._clock.now()
        squad = [
            SquadMember(player, _contract_view(contracts.get(player.id), now)) for player in players
        ]
        squad_value = calculate_squad_value(player.market_value for player in players)
        return ClubDetails(ClubView(club, squad_value), squad)


def _contract_view(contract: Contract | None, now: datetime) -> ContractView | None:
    if contract is None:
        return None
    days = remaining_days(contract.loyalty_until, now)
    return ContractView(
        purchase_value=contract.purchase_value,
        loyalty_until=contract.loyalty_until,
        remaining_days=days,
        penalty_percent=penalty_percent(days),
    )
