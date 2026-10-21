from collections.abc import Sequence
from typing import Protocol


class LineupRepository(Protocol):
    def list_player_ids(self, club_id: int) -> list[int]:
        """Devolve os ids dos titulares do clube, em qualquer ordem."""

    def replace(self, club_id: int, player_ids: Sequence[int]) -> None:
        """Troca a escalação inteira do clube pelos jogadores informados."""

    def remove_player(self, player_id: int) -> None:
        """Tira o jogador da escalação, se ele estiver nela."""
