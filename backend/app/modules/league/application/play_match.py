from app.modules.clubs.application.public_operations import ClubsPublicOperations
from app.modules.league.application.get_lineup import GetLineup
from app.modules.league.application.lineup_details import LineupDetails
from app.modules.league.application.match_view import MatchView
from app.modules.league.domain.duels import Starter, Team
from app.modules.league.domain.errors import LineupIncomplete, SameClubMatch
from app.modules.league.domain.match import Match
from app.modules.league.ports.repositories import MatchRepository
from app.modules.players.application.public_operations import PlayerView
from app.shared.application.clock import Clock
from app.shared.application.unit_of_work import UnitOfWork


class PlayMatch:
    def __init__(
        self,
        lineups: GetLineup,
        clubs: ClubsPublicOperations,
        matches: MatchRepository,
        clock: Clock,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._lineups = lineups
        self._clubs = clubs
        self._matches = matches
        self._clock = clock
        self._unit_of_work = unit_of_work

    def execute(self, home_club_id: int, away_club_id: int) -> MatchView:
        if home_club_id == away_club_id:
            raise SameClubMatch("O mandante e o visitante precisam ser clubes diferentes.")
        home = self._lineups.execute(home_club_id)
        away = self._lineups.execute(away_club_id)
        _ensure_can_play(home)
        _ensure_can_play(away)
        match = Match.play(_to_team(home), _to_team(away), self._clock.now())
        saved_match = self._matches.add(match)
        view = MatchView.of(saved_match, self._clubs.list_club_names())
        self._unit_of_work.commit()
        return view


def _ensure_can_play(lineup: LineupDetails) -> None:
    if not lineup.complete:
        raise LineupIncomplete(f"O clube {lineup.club_id} não tem a escalação completa.")


def _to_team(lineup: LineupDetails) -> Team:
    starters = [_to_starter(view) for view in lineup.players]
    return Team.from_starters(lineup.club_id, lineup.formation, starters)


def _to_starter(view: PlayerView) -> Starter:
    return Starter(
        player_id=view.id,
        name=view.name,
        position=view.position,
        condition=view.condition,
        shooting=view.attributes.shooting,
        passing=view.attributes.passing,
        dribbling=view.attributes.dribbling,
        defending=view.attributes.defending,
    )
