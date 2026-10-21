from collections.abc import Sequence
from typing import Protocol

from app.modules.league.domain.match import Match


class LineupRepository(Protocol):
    def list_player_ids(self, club_id: int) -> list[int]:
        """Devolve os ids dos titulares do clube, em qualquer ordem."""

    def replace(self, club_id: int, player_ids: Sequence[int]) -> None:
        """Troca a escalação inteira do clube pelos jogadores informados."""

    def remove_player(self, player_id: int) -> None:
        """Tira o jogador da escalação, se ele estiver nela."""


class MatchRepository(Protocol):
    def add(self, match: Match) -> Match:
        """Grava a partida e os 6 duelos e a devolve com o id preenchido."""

    def get(self, match_id: int) -> Match | None:
        """Devolve a partida com os duelos na ordem, ou None se não existir."""

    def list_matches(self, club_id: int | None) -> list[Match]:
        """Devolve as partidas sem os duelos, da mais recente para a mais antiga.

        Com club_id, só as partidas em que o clube foi mandante ou visitante.
        Em empate de data e hora, o maior id vem primeiro.
        """
