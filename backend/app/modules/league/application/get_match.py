from app.modules.clubs.application.public_operations import ClubsPublicOperations
from app.modules.league.application.match_view import MatchView
from app.modules.league.domain.errors import MatchNotFound
from app.modules.league.ports.repositories import MatchRepository


class GetMatch:
    def __init__(self, clubs: ClubsPublicOperations, matches: MatchRepository) -> None:
        self._clubs = clubs
        self._matches = matches

    def execute(self, match_id: int) -> MatchView:
        match = self._matches.get(match_id)
        if match is None:
            raise MatchNotFound("Partida não encontrada.")
        return MatchView.of(match, self._clubs.list_club_names())
