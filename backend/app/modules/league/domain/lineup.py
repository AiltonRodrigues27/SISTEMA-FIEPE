from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass

from app.modules.league.domain.errors import (
    PlayerNotInSquad,
    PlayerUnavailable,
    PositionsDoNotFormFormation,
)
from app.modules.league.domain.formations import FORMATIONS, FormationShape
from app.modules.players.domain.enums import Position

DEFENSE_POSITIONS = (Position.ZAG, Position.LAT)


@dataclass(frozen=True)
class LineupCandidate:
    player_id: int
    club_id: int | None
    position: Position
    can_play: bool


def ensure_valid_lineup(
    club_id: int, formation: str, candidates: Sequence[LineupCandidate]
) -> None:
    for candidate in candidates:
        if candidate.club_id != club_id:
            raise PlayerNotInSquad(f"O jogador {candidate.player_id} não é do elenco do clube.")
    for candidate in candidates:
        if not candidate.can_play:
            raise PlayerUnavailable(f"O jogador {candidate.player_id} está DOENTE.")
    _ensure_positions_fit(formation, [candidate.position for candidate in candidates])


def _ensure_positions_fit(formation: str, positions: Sequence[Position]) -> None:
    shape = FORMATIONS[formation]
    counts = Counter(positions)
    actual = FormationShape(
        defense=sum(counts[position] for position in DEFENSE_POSITIONS),
        midfield=counts[Position.MEI],
        attack=counts[Position.ATA],
    )
    if counts[Position.GOL] != 1 or actual != shape:
        raise PositionsDoNotFormFormation(
            f"As posições não fecham a formação {formation}: "
            f"1 GOL, {shape.defense} ZAG ou LAT, {shape.midfield} MEI e {shape.attack} ATA."
        )
