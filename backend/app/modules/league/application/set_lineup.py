from collections.abc import Sequence

from app.modules.clubs.application.public_operations import ClubsPublicOperations
from app.modules.league.application.lineup_details import LineupDetails, load_lineup_details
from app.modules.league.domain.lineup import LineupCandidate, ensure_valid_lineup
from app.modules.league.ports.repositories import LineupRepository
from app.modules.players.application.public_operations import PlayersPublicOperations
from app.shared.application.unit_of_work import UnitOfWork


class SetLineup:
    def __init__(
        self,
        players: PlayersPublicOperations,
        clubs: ClubsPublicOperations,
        lineups: LineupRepository,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._players = players
        self._clubs = clubs
        self._lineups = lineups
        self._unit_of_work = unit_of_work

    def execute(self, club_id: int, formation: str, player_ids: Sequence[int]) -> LineupDetails:
        self._clubs.get_account(club_id)
        candidates = [self._build_candidate(player_id) for player_id in player_ids]
        ensure_valid_lineup(club_id, formation, candidates)
        self._lineups.replace(club_id, player_ids)
        self._clubs.set_formation(club_id, formation)
        details = load_lineup_details(club_id, self._players, self._clubs, self._lineups)
        self._unit_of_work.commit()
        return details

    def _build_candidate(self, player_id: int) -> LineupCandidate:
        view = self._players.get_view(player_id)
        return LineupCandidate(
            player_id=view.id,
            club_id=view.club_id,
            position=view.position,
            can_play=view.condition.can_play,
        )
