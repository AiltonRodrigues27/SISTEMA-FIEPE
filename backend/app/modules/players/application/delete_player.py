from app.modules.players.application.player_lookup import get_existing_player
from app.modules.players.ports.repositories import PlayerRepository
from app.shared.application.unit_of_work import UnitOfWork


class DeletePlayer:
    def __init__(self, players: PlayerRepository, unit_of_work: UnitOfWork) -> None:
        self._players = players
        self._unit_of_work = unit_of_work

    def execute(self, player_id: int) -> None:
        player = get_existing_player(self._players, player_id)
        player.ensure_can_be_deleted()
        self._players.mark_deleted(player_id)
        self._unit_of_work.commit()
