from app.modules.clubs.application.public_operations import ClubsPublicOperations
from app.modules.league.application.match_view import MatchView
from app.modules.league.ports.repositories import MatchRepository


class ListMatches:
    def __init__(self, clubs: ClubsPublicOperations, matches: MatchRepository) -> None:
        self._clubs = clubs
        self._matches = matches

    def execute(self, club_id: int | None) -> list[MatchView]:
        if club_id is not None:
            self._clubs.get_account(club_id)
        club_names = self._clubs.list_club_names()
        found = self._matches.list_matches(club_id)
        return [MatchView.of(match, club_names) for match in found]
