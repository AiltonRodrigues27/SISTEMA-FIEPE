from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from app.modules.clubs.application.public_operations import (
    ClubsPublicOperations,
    PlayerSigning,
    SignedContract,
)
from app.modules.market.domain.calculations import calculate_purchase_fee, ensure_within_cash_limit
from app.modules.market.domain.errors import PlayerAlreadySoldByClub
from app.modules.market.domain.transaction import Transaction
from app.modules.market.ports.repositories import TransactionRepository
from app.modules.players.application.public_operations import PlayersPublicOperations
from app.shared.application.clock import Clock
from app.shared.application.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class PurchaseResult:
    transaction: Transaction
    contract: SignedContract
    club_cash: Decimal


class BuyPlayer:
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

    def execute(self, player_id: int, club_id: int, loyalty_until: datetime) -> PurchaseResult:
        player = self._players.get_free_player(player_id)
        account = self._clubs.get_account(club_id)
        if self._transactions.club_sold_player(club_id, player_id):
            raise PlayerAlreadySoldByClub(
                "O clube não pode comprar de volta um jogador que vendeu."
            )
        fee = calculate_purchase_fee(player.market_value)
        total_cost = player.market_value + fee
        ensure_within_cash_limit(total_cost, account.cash)
        now = self._clock.now()
        signing = PlayerSigning(
            club_id=club_id,
            player_id=player_id,
            purchase_value=player.market_value,
            total_cost=total_cost,
            loyalty_until=loyalty_until,
        )
        contract = self._clubs.sign_player(signing, now)
        self._players.assign_to_club(player_id, club_id)
        transaction = self._transactions.add(
            Transaction.purchase(
                club_id=club_id,
                player_id=player_id,
                player_name=player.name,
                value=player.market_value,
                fee=fee,
                created_at=now,
            )
        )
        self._unit_of_work.commit()
        return PurchaseResult(transaction, contract, account.cash - total_cost)
