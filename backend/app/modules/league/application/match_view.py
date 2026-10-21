from collections.abc import Mapping
from dataclasses import dataclass
from typing import Self

from app.modules.league.domain.match import Match


@dataclass(frozen=True)
class MatchView:
    match: Match
    home_club_name: str
    away_club_name: str

    @classmethod
    def of(cls, match: Match, club_names: Mapping[int, str]) -> Self:
        return cls(match, club_names[match.home_club_id], club_names[match.away_club_id])
