from dataclasses import dataclass

from app.modules.clubs.application.public_operations import ClubsPublicOperations
from app.modules.league.domain.formations import LINEUP_SIZE
from app.modules.league.ports.repositories import LineupRepository
from app.modules.players.application.public_operations import PlayersPublicOperations, PlayerView


@dataclass(frozen=True)
class LineupDetails:
    club_id: int
    formation: str | None
    players: list[PlayerView]

    @property
    def complete(self) -> bool:
        return len(self.players) == LINEUP_SIZE


def load_lineup_details(
    club_id: int,
    players: PlayersPublicOperations,
    clubs: ClubsPublicOperations,
    lineups: LineupRepository,
) -> LineupDetails:
    starter_ids = set(lineups.list_player_ids(club_id))
    squad = players.list_by_club(club_id)
    starters = [view for view in squad if view.id in starter_ids]
    return LineupDetails(club_id, clubs.get_formation(club_id), starters)
