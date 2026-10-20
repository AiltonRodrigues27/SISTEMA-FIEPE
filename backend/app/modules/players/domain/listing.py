from collections.abc import Callable, Sequence
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from app.modules.players.domain.entities import Player
from app.modules.players.domain.enums import PhysicalCondition, Position
from app.shared.domain.text import normalize_text

POSITION_ORDER = {
    Position.GOL: 0,
    Position.ZAG: 1,
    Position.LAT: 2,
    Position.MEI: 3,
    Position.ATA: 4,
}


class SortKey(StrEnum):
    NAME = "name"
    VALUE_ASC = "value_asc"
    VALUE_DESC = "value_desc"
    AGE_ASC = "age_asc"
    AGE_DESC = "age_desc"
    POSITION = "position"


@dataclass(frozen=True)
class PlayerFilters:
    search: str | None = None
    position: Position | None = None
    condition: PhysicalCondition | None = None
    free: bool | None = None
    club_id: int | None = None
    min_age: int | None = None
    max_age: int | None = None
    min_value: Decimal | None = None
    max_value: Decimal | None = None


def matches(player: Player, filters: PlayerFilters) -> bool:
    checks = (
        filters.search is None or normalize_text(filters.search) in normalize_text(player.name),
        filters.position is None or player.position is filters.position,
        filters.condition is None or player.condition is filters.condition,
        filters.free is None or player.is_free == filters.free,
        filters.club_id is None or player.club_id == filters.club_id,
        filters.min_age is None or player.age >= filters.min_age,
        filters.max_age is None or player.age <= filters.max_age,
        filters.min_value is None or player.market_value >= filters.min_value,
        filters.max_value is None or player.market_value <= filters.max_value,
    )
    return all(checks)


def sort_players(players: Sequence[Player], criteria: Sequence[SortKey]) -> list[Player]:
    ordered = sorted(players, key=_name_then_id)
    for criterion in reversed(criteria):
        key, descending = _CRITERIA[criterion]
        ordered.sort(key=key, reverse=descending)
    return ordered


def _name_then_id(player: Player) -> tuple[str, int | None]:
    return normalize_text(player.name), player.id


_CRITERIA: dict[SortKey, tuple[Callable[[Player], object], bool]] = {
    SortKey.NAME: (lambda player: normalize_text(player.name), False),
    SortKey.VALUE_ASC: (lambda player: player.market_value, False),
    SortKey.VALUE_DESC: (lambda player: player.market_value, True),
    SortKey.AGE_ASC: (lambda player: player.age, False),
    SortKey.AGE_DESC: (lambda player: player.age, True),
    SortKey.POSITION: (lambda player: POSITION_ORDER[player.position], False),
}
