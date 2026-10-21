from typing import Protocol


class LineupGateway(Protocol):
    def remove_player(self, player_id: int) -> None:
        """Tira o jogador da escalação do clube, se ele estiver nela."""
