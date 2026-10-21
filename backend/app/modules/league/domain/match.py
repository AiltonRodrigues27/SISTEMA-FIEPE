from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Self

from app.modules.league.domain.duels import Duel, Team, count_goals, play_duels


class MatchResult(StrEnum):
    MANDANTE = "MANDANTE"
    VISITANTE = "VISITANTE"
    EMPATE = "EMPATE"


@dataclass(frozen=True)
class Match:
    id: int | None
    home_club_id: int
    away_club_id: int
    home_goals: int
    away_goals: int
    home_formation: str
    away_formation: str
    played_at: datetime
    duels: tuple[Duel, ...]

    @classmethod
    def play(cls, home: Team, away: Team, played_at: datetime) -> Self:
        duels = tuple(play_duels(home, away))
        return cls(
            id=None,
            home_club_id=home.club_id,
            away_club_id=away.club_id,
            home_goals=count_goals(duels, home.club_id),
            away_goals=count_goals(duels, away.club_id),
            home_formation=home.formation,
            away_formation=away.formation,
            played_at=played_at,
            duels=duels,
        )

    @property
    def result(self) -> MatchResult:
        if self.home_goals > self.away_goals:
            return MatchResult.MANDANTE
        if self.home_goals < self.away_goals:
            return MatchResult.VISITANTE
        return MatchResult.EMPATE
