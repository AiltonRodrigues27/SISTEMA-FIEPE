from app.modules.clubs.application.public_operations import ClubsPublicOperations
from app.modules.league.domain.standings import StandingsRow, calculate_standings
from app.modules.league.ports.repositories import MatchRepository


class GetStandings:
    def __init__(self, clubs: ClubsPublicOperations, matches: MatchRepository) -> None:
        self._clubs = clubs
        self._matches = matches

    def execute(self) -> list[StandingsRow]:
        club_names = self._clubs.list_club_names()
        return calculate_standings(club_names, self._matches.list_matches(None))
