from typing import Protocol

from app.modules.players.domain.entities import Player


class PlayerRepository(Protocol):
    def add(self, player: Player) -> Player:
        """Grava o jogador novo e o devolve com o id preenchido."""

    def get(self, player_id: int) -> Player | None:
        """Devolve o jogador ativo, ou None se não existir ou estiver excluído."""

    def list_active(self) -> list[Player]:
        """Devolve todos os jogadores ativos, sem os excluídos, em qualquer ordem."""

    def update(self, player: Player) -> None:
        """Grava as mudanças de um jogador que já existe."""

    def mark_deleted(self, player_id: int) -> None:
        """Marca o jogador como excluído, sem apagar a linha."""
