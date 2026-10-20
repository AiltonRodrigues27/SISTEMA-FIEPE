from collections.abc import Iterable, Sequence
from decimal import Decimal
from enum import StrEnum

from app.modules.clubs.domain.entities import ClubView
from app.shared.domain.text import normalize_text


class ClubSortKey(StrEnum):
    NAME = "name"
    NET_WORTH_ASC = "net_worth_asc"
    NET_WORTH_DESC = "net_worth_desc"


def calculate_squad_value(market_values: Iterable[Decimal]) -> Decimal:
    return sum(market_values, Decimal("0.00"))


def sort_clubs(views: Sequence[ClubView], key: ClubSortKey) -> list[ClubView]:
    ordered = sorted(views, key=lambda view: (normalize_text(view.club.name), view.club.id))
    if key is ClubSortKey.NET_WORTH_ASC:
        ordered.sort(key=lambda view: view.net_worth)
    elif key is ClubSortKey.NET_WORTH_DESC:
        ordered.sort(key=lambda view: view.net_worth, reverse=True)
    return ordered
