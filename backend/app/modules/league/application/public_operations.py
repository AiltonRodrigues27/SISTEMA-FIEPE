from app.modules.league.ports.repositories import LineupRepository


class LeaguePublicOperations:
    def __init__(self, lineups: LineupRepository) -> None:
        self._lineups = lineups

    def remove_player(self, player_id: int) -> None:
        self._lineups.remove_player(player_id)
