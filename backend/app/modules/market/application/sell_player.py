from dataclasses import dataclass
from decimal import Decimal

from app.modules.clubs.application.public_operations import (
    ClubsPublicOperations,
    ContractTermination,
)
from app.modules.market.domain.calculations import calculate_sale_outcome
from app.modules.market.domain.transaction import Transaction
from app.modules.market.ports.repositories import TransactionRepository
from app.modules.players.application.public_operations import PlayersPublicOperations
from app.shared.application.clock import Clock
from app.shared.application.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class SaleResult:
    transaction: Transaction
    termination: ContractTermination
    club_cash: Decimal


class SellPlayer:
    def __init__(
        self,
        players: PlayersPublicOperations,
        clubs: ClubsPublicOperations,
        transactions: TransactionRepository,
        clock: Clock,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._players = players
        self._clubs = clubs
        self._transactions = transactions
        self._clock = clock
        self._unit_of_work = unit_of_work

    def execute(self, player_id: int) -> SaleResult:
        player = self._players.get_player_with_club(player_id)
        now = self._clock.now()
        termination = self._clubs.terminate_contract(player_id, player.market_value, now)
        outcome = calculate_sale_outcome(
            player.market_value, termination.purchase_value, termination.penalty
        )
        self._players.release_from_club(player_id)
        club_cash = self._clubs.credit_cash(player.club_id, outcome.credit)
        transaction = self._transactions.add(
            Transaction.sale(
                club_id=player.club_id,
                player_id=player_id,
                player_name=player.name,
                outcome=outcome,
                created_at=now,
            )
        )
        self._unit_of_work.commit()
        return SaleResult(transaction, termination, club_cash)
