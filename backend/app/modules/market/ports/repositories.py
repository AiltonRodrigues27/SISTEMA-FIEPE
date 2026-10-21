from typing import Protocol

from app.modules.market.domain.transaction import Transaction


class TransactionRepository(Protocol):
    def add(self, transaction: Transaction) -> Transaction:
        """Grava a transação nova e a devolve com o id preenchido."""

    def club_sold_player(self, club_id: int, player_id: int) -> bool:
        """Diz se o clube já vendeu esse jogador alguma vez."""
