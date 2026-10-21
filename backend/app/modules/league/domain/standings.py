from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace

from app.modules.league.domain.match import Match
from app.shared.domain.text import normalize_text

POINTS_FOR_WIN = 3
POINTS_FOR_DRAW = 1
UNRANKED = 0


@dataclass(frozen=True)
class StandingsRow:
    position: int
    club_id: int
    club_name: str
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int

    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against

    @property
    def points(self) -> int:
        return self.wins * POINTS_FOR_WIN + self.draws * POINTS_FOR_DRAW


@dataclass
class _Tally:
    wins: int = 0
    draws: int = 0
    losses: int = 0
    goals_for: int = 0
    goals_against: int = 0

    def register(self, goals_for: int, goals_against: int) -> None:
        self.goals_for += goals_for
        self.goals_against += goals_against
        if goals_for > goals_against:
            self.wins += 1
        elif goals_for < goals_against:
            self.losses += 1
        else:
            self.draws += 1


def calculate_standings(
    club_names: Mapping[int, str], matches: Sequence[Match]
) -> list[StandingsRow]:
    tallies = {club_id: _Tally() for club_id in club_names}
    for match in matches:
        tallies[match.home_club_id].register(match.home_goals, match.away_goals)
        tallies[match.away_club_id].register(match.away_goals, match.home_goals)
    rows = [_to_row(club_id, name, tallies[club_id]) for club_id, name in club_names.items()]
    rows.sort(key=_ranking_key)
    return [replace(row, position=position) for position, row in enumerate(rows, start=1)]


def _to_row(club_id: int, club_name: str, tally: _Tally) -> StandingsRow:
    return StandingsRow(
        position=UNRANKED,
        club_id=club_id,
        club_name=club_name,
        played=tally.wins + tally.draws + tally.losses,
        wins=tally.wins,
        draws=tally.draws,
        losses=tally.losses,
        goals_for=tally.goals_for,
        goals_against=tally.goals_against,
    )


def _ranking_key(row: StandingsRow) -> tuple[int, int, int, str, int]:
    return (
        -row.points,
        -row.goal_difference,
        -row.goals_for,
        normalize_text(row.club_name),
        row.club_id,
    )
