from app.modules.players.domain.entities import Player, PlayerRegistration
from app.modules.players.ports.repositories import PlayerRepository
from app.shared.application.unit_of_work import UnitOfWork


class CreatePlayer:
    def __init__(self, players: PlayerRepository, unit_of_work: UnitOfWork) -> None:
        self._players = players
        self._unit_of_work = unit_of_work

    def execute(self, registration: PlayerRegistration) -> Player:
        player = Player.register(registration)
        saved_player = self._players.add(player)
        self._unit_of_work.commit()
        return saved_player
