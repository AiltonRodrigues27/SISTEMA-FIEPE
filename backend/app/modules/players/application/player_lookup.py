from app.modules.players.domain.entities import Player
from app.modules.players.domain.errors import PlayerNotFound
from app.modules.players.ports.repositories import PlayerRepository


def get_existing_player(players: PlayerRepository, player_id: int) -> Player:
    player = players.get(player_id)
    if player is None:
        raise PlayerNotFound("Jogador não encontrado.")
    return player
