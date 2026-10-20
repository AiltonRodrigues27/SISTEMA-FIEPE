from app.modules.clubs.application.list_clubs import ListClubs
from app.modules.clubs.domain.listing import ClubSortKey


def names(views) -> list[str]:
    return [view.club.name for view in views]


def test_list_clubs_sorts_by_name_by_default_ignoring_accents(
    club_repository, players_operations, add_club
) -> None:
    add_club("Zebras FC", "ZFC")
    add_club("Águias FC", "AGU")
    add_club("Beta FC", "BFC")

    views = ListClubs(club_repository, players_operations).execute(ClubSortKey.NAME)

    assert names(views) == ["Águias FC", "Beta FC", "Zebras FC"]


def test_list_clubs_computes_squad_value_and_net_worth_from_the_market_values(
    club_repository, players_operations, add_club, make_view
) -> None:
    eagles = add_club("Águias FC", "AGU")
    add_club("Beta FC", "BFC")
    players_operations.views = [
        make_view(1, "Ana Lima", eagles.id, "40.00"),
        make_view(2, "Beto Souza", eagles.id, "30.50"),
    ]

    views = ListClubs(club_repository, players_operations).execute(ClubSortKey.NAME)

    assert [str(view.squad_value) for view in views] == ["70.50", "0.00"]
    assert [str(view.net_worth) for view in views] == ["370.50", "300.00"]


def test_list_clubs_sorts_by_net_worth(
    club_repository, players_operations, add_club, make_view
) -> None:
    rich = add_club("Alfa FC", "AFC")
    poor = add_club("Beta FC", "BFC")
    middle = add_club("Gama FC", "GFC")
    players_operations.views = [
        make_view(1, "Ana Lima", rich.id, "70.00"),
        make_view(2, "Beto Souza", middle.id, "50.00"),
    ]
    use_case = ListClubs(club_repository, players_operations)

    ascending = use_case.execute(ClubSortKey.NET_WORTH_ASC)
    descending = use_case.execute(ClubSortKey.NET_WORTH_DESC)

    assert names(ascending) == [poor.name, middle.name, rich.name]
    assert names(descending) == [rich.name, middle.name, poor.name]


def test_list_clubs_breaks_net_worth_ties_by_name(
    club_repository, players_operations, add_club
) -> None:
    add_club("Beta FC", "BFC")
    add_club("Alfa FC", "AFC")

    views = ListClubs(club_repository, players_operations).execute(ClubSortKey.NET_WORTH_DESC)

    assert names(views) == ["Alfa FC", "Beta FC"]


def test_list_clubs_without_clubs_is_empty(club_repository, players_operations) -> None:
    assert ListClubs(club_repository, players_operations).execute(ClubSortKey.NAME) == []
