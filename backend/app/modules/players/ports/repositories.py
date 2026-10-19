from typing import Protocol

from app.modules.players.domain.entities import Player


class PlayerRepository(Protocol):
    def add(self, player: Player) -> Player:
        """Grava o jogador novo e o devolve com o id preenchido."""

    def get(self, player_id: int) -> Player | None:
        """Devolve o jogador ativo, ou None se não existir ou estiver excluído."""
