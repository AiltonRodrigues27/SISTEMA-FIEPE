from typing import Annotated, Self

from pydantic import AfterValidator, BaseModel

from app.api.strict_types import ResourceId
from app.modules.league.application.lineup_details import LineupDetails
from app.modules.league.domain.formations import FORMATIONS, LINEUP_SIZE
from app.modules.players.adapters.inbound.http.schemas import PlayerResponse


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
