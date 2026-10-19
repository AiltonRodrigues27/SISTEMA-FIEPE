from app.modules.players.domain.entities import Player
from app.modules.players.domain.errors import PlayerNotFound
from app.modules.players.ports.repositories import PlayerRepository


class GetPlayer:
    def __init__(self, players: PlayerRepository) -> None:
        self._players = players

    def execute(self, player_id: int) -> Player:
        player = self._players.get(player_id)
        if player is None:
            raise PlayerNotFound("Jogador não encontrado.")
        return player
