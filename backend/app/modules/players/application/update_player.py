from dataclasses import dataclass

from app.modules.players.application.player_lookup import get_existing_player
from app.modules.players.domain.entities import Player
from app.modules.players.domain.enums import Position
from app.modules.players.ports.repositories import PlayerRepository
from app.shared.application.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class PlayerProfileChanges:
    name: str
    position: Position
    agility: int
    age: int


class UpdatePlayer:
    def __init__(self, players: PlayerRepository, unit_of_work: UnitOfWork) -> None:
        self._players = players
        self._unit_of_work = unit_of_work

    def execute(self, player_id: int, changes: PlayerProfileChanges) -> Player:
        player = get_existing_player(self._players, player_id)
        player.update_profile(changes.name, changes.position, changes.agility, changes.age)
        self._players.update(player)
        self._unit_of_work.commit()
        return player
