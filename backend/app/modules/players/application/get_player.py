from app.modules.players.application.player_lookup import get_existing_player
from app.modules.players.domain.entities import Player
from app.modules.players.ports.repositories import PlayerRepository


class GetPlayer:
    def __init__(self, players: PlayerRepository) -> None:
        self._players = players

    def execute(self, player_id: int) -> Player:
        return get_existing_player(self._players, player_id)
