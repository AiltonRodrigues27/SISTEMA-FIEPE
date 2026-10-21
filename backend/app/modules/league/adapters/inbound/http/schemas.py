from typing import Annotated, Self

from pydantic import AfterValidator, BaseModel

from app.api.strict_types import ResourceId
from app.modules.league.application.lineup_details import LineupDetails
from app.modules.league.application.match_view import MatchView
from app.modules.league.domain.duels import Duel, DuelPlayer
from app.modules.league.domain.formations import FORMATIONS, LINEUP_SIZE
from app.modules.league.domain.standings import StandingsRow
from app.modules.players.adapters.inbound.http.schemas import PlayerResponse
from app.shared.domain.brasilia_time import format_api_datetime


def _ensure_known_formation(value: str) -> str:
    if value not in FORMATIONS:
        raise ValueError(f"use uma destas formações: {', '.join(FORMATIONS)}")
    return value


def _ensure_distinct_starters(player_ids: list[int]) -> list[int]:
    if len(player_ids) != LINEUP_SIZE or len(set(player_ids)) != LINEUP_SIZE:
        raise ValueError(f"deve ter exatamente {LINEUP_SIZE} ids distintos")
    return player_ids


Formation = Annotated[str, AfterValidator(_ensure_known_formation)]
StarterIds = Annotated[list[ResourceId], AfterValidator(_ensure_distinct_starters)]


class SetLineupRequest(BaseModel):
    formation: Formation
    player_ids: StarterIds


class LineupResponse(BaseModel):
    club_id: int
    formation: str | None
    complete: bool
    players: list[PlayerResponse]

    @classmethod
    def from_details(cls, details: LineupDetails) -> Self:
        return cls(
            club_id=details.club_id,
            formation=details.formation,
            complete=details.complete,
            players=[PlayerResponse.from_view(view) for view in details.players],
        )


class PlayMatchRequest(BaseModel):
    home_club_id: ResourceId
    away_club_id: ResourceId


class MatchSideResponse(BaseModel):
    club_id: int
    club_name: str
    formation: str
    goals: int


class DuelPlayerResponse(BaseModel):
    player_id: int
    player_name: str
    position: str
    condition: str
    attribute: str
    value: int

    @classmethod
    def from_duel_player(cls, player: DuelPlayer) -> Self:
        return cls(
            player_id=player.player_id,
            player_name=player.player_name,
            position=player.position.value,
            condition=player.condition.value,
            attribute=player.attribute,
            value=player.value,
        )


class DuelResponse(BaseModel):
    order: int
    attacking_club_id: int
    attacker: DuelPlayerResponse
    defender: DuelPlayerResponse
    goal: bool

    @classmethod
    def from_duel(cls, duel: Duel) -> Self:
        return cls(
            order=duel.order,
            attacking_club_id=duel.attacking_club_id,
            attacker=DuelPlayerResponse.from_duel_player(duel.attacker),
            defender=DuelPlayerResponse.from_duel_player(duel.defender),
            goal=duel.goal,
        )


class MatchSummaryResponse(BaseModel):
    id: int
    played_at: str
    home: MatchSideResponse
    away: MatchSideResponse
    result: str

    @classmethod
    def from_view(cls, view: MatchView) -> Self:
        return cls(**_summary_fields(view))


class MatchResponse(MatchSummaryResponse):
    duels: list[DuelResponse]

    @classmethod
    def from_view(cls, view: MatchView) -> Self:
        duels = [DuelResponse.from_duel(duel) for duel in view.match.duels]
        return cls(**_summary_fields(view), duels=duels)


class StandingsRowResponse(BaseModel):
    position: int
    club_id: int
    club_name: str
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int

    @classmethod
    def from_row(cls, row: StandingsRow) -> Self:
        return cls(
            position=row.position,
            club_id=row.club_id,
            club_name=row.club_name,
            played=row.played,
            wins=row.wins,
            draws=row.draws,
            losses=row.losses,
            goals_for=row.goals_for,
            goals_against=row.goals_against,
            goal_difference=row.goal_difference,
            points=row.points,
        )


def _summary_fields(view: MatchView) -> dict:
    match = view.match
    return {
        "id": match.id,
        "played_at": format_api_datetime(match.played_at),
        "home": MatchSideResponse(
            club_id=match.home_club_id,
            club_name=view.home_club_name,
            formation=match.home_formation,
            goals=match.home_goals,
        ),
        "away": MatchSideResponse(
            club_id=match.away_club_id,
            club_name=view.away_club_name,
            formation=match.away_formation,
            goals=match.away_goals,
        ),
        "result": match.result.value,
    }
