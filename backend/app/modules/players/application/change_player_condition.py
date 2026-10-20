from app.modules.players.application.player_lookup import get_existing_player
from app.modules.players.domain.entities import Player
from app.modules.players.domain.enums import PhysicalCondition
from app.modules.players.ports.repositories import PlayerRepository
from app.shared.application.unit_of_work import UnitOfWork


class ChangePlayerCondition:
    def __init__(self, players: PlayerRepository, unit_of_work: UnitOfWork) -> None:
        self._players = players
        self._unit_of_work = unit_of_work

    def execute(self, player_id: int, condition: PhysicalCondition) -> Player:
        player = get_existing_player(self._players, player_id)
        player.change_condition(condition)
        self._players.update(player)
        self._unit_of_work.commit()
        return player
