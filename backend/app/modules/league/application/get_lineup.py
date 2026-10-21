from app.modules.clubs.application.public_operations import ClubsPublicOperations
from app.modules.league.application.lineup_details import LineupDetails, load_lineup_details
from app.modules.league.ports.repositories import LineupRepository
from app.modules.players.application.public_operations import PlayersPublicOperations


class GetLineup:
    def __init__(
        self,
        players: PlayersPublicOperations,
        clubs: ClubsPublicOperations,
        lineups: LineupRepository,
    ) -> None:
        self._players = players
        self._clubs = clubs
        self._lineups = lineups

    def execute(self, club_id: int) -> LineupDetails:
        self._clubs.get_account(club_id)
        return load_lineup_details(club_id, self._players, self._clubs, self._lineups)
