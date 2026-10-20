from decimal import Decimal

from app.modules.clubs.domain.entities import Club, ClubView
from app.modules.clubs.domain.listing import ClubSortKey, calculate_squad_value, sort_clubs


def build_view(club_id: int, name: str, cash: str, squad_value: str = "0.00") -> ClubView:
    club = Club(id=club_id, name=name, acronym="AAA", cash=Decimal(cash), formation=None)
    return ClubView(club, Decimal(squad_value))


def names(views: list[ClubView]) -> list[str]:
    return [view.club.name for view in views]


def test_squad_value_is_the_sum_of_the_market_values() -> None:
    assert calculate_squad_value([Decimal("37.00"), Decimal("40.50")]) == Decimal("77.50")


def test_squad_value_of_an_empty_squad_is_zero() -> None:
    assert calculate_squad_value([]) == Decimal("0.00")


def test_sort_by_name_ignores_case_and_accents() -> None:
    views = [
        build_view(1, "Zebras FC", "300.00"),
        build_view(2, "Águias FC", "300.00"),
        build_view(3, "beta FC", "300.00"),
    ]

    assert names(sort_clubs(views, ClubSortKey.NAME)) == ["Águias FC", "beta FC", "Zebras FC"]


def test_sort_by_net_worth_uses_cash_plus_squad_value() -> None:
    views = [
        build_view(1, "Alfa FC", "300.00", "70.00"),
        build_view(2, "Beta FC", "300.00"),
        build_view(3, "Gama FC", "250.00", "100.00"),
    ]

    ascending = sort_clubs(views, ClubSortKey.NET_WORTH_ASC)
    descending = sort_clubs(views, ClubSortKey.NET_WORTH_DESC)

    assert names(ascending) == ["Beta FC", "Gama FC", "Alfa FC"]
    assert names(descending) == ["Alfa FC", "Gama FC", "Beta FC"]


def test_sort_by_net_worth_breaks_ties_by_name_then_id() -> None:
    views = [
        build_view(3, "Beta FC", "300.00"),
        build_view(2, "Alfa FC", "300.00"),
        build_view(1, "Alfa FC", "300.00"),
    ]

    result = sort_clubs(views, ClubSortKey.NET_WORTH_DESC)

    assert [view.club.id for view in result] == [1, 2, 3]
