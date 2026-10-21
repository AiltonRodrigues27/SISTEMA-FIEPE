from dataclasses import dataclass

from app.modules.clubs.application.public_operations import ClubsPublicOperations
from app.modules.market.domain.history import TransactionFilters, TransactionSummary, summarize
from app.modules.market.domain.transaction import Transaction
from app.modules.market.ports.repositories import TransactionRepository
from app.modules.players.application.public_operations import PlayersPublicOperations


@dataclass(frozen=True)
class TransactionHistory:
    transactions: list[Transaction]
    summary: TransactionSummary


class ListTransactions:
    def __init__(
        self,
        players: PlayersPublicOperations,
        clubs: ClubsPublicOperations,
        transactions: TransactionRepository,
    ) -> None:
        self._players = players
        self._clubs = clubs
        self._transactions = transactions

    def execute(self, club_id: int, filters: TransactionFilters) -> TransactionHistory:
        self._clubs.get_account(club_id)
        if filters.player_id is not None:
            self._players.get_view(filters.player_id)
        found = self._transactions.list_by_club(club_id, filters)
        return TransactionHistory(found, summarize(found))
