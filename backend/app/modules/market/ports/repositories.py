from typing import Protocol

from app.modules.market.domain.history import TransactionFilters
from app.modules.market.domain.transaction import Transaction


class TransactionRepository(Protocol):
    def add(self, transaction: Transaction) -> Transaction:
        """Grava a transação nova e a devolve com o id preenchido."""

    def club_sold_player(self, club_id: int, player_id: int) -> bool:
        """Diz se o clube já vendeu esse jogador alguma vez."""

    def list_by_club(self, club_id: int, filters: TransactionFilters) -> list[Transaction]:
        """Devolve as transações do clube que atendem aos filtros, da mais recente à mais antiga.

        O empate de data e hora é desfeito pelo id decrescente.
        """
