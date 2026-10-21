import pytest

from app.modules.clubs.domain.errors import ClubNotFound
from app.modules.league.application.get_lineup import GetLineup


def build_use_case(players_operations, clubs_operations, lineups) -> GetLineup:
    return GetLineup(players_operations, clubs_operations, lineups)


def test_get_lineup_of_a_club_without_lineup_is_empty_and_incomplete(
    players_operations, clubs_operations, lineups, squad
) -> None:
    details = build_use_case(players_operations, clubs_operations, lineups).execute(1)

    assert details.club_id == 1
    assert details.formation is None
    assert details.players == []
    assert details.complete is False


def test_get_lineup_returns_the_five_starters_in_squad_order(
    players_operations, clubs_operations, lineups, squad
) -> None:
    lineups.replace(1, [34, 31, 30, 33, 32])
    clubs_operations.set_formation(1, "2-1-1")

    details = build_use_case(players_operations, clubs_operations, lineups).execute(1)

    assert [view.name for view in details.players] == [
        "Rui Prado",
        "Teo Brandao",
        "Davi Lins",
        "Lauro Neves",
        "Otto Rangel",
    ]
    assert (details.formation, details.complete) == ("2-1-1", True)


def test_get_lineup_keeps_the_formation_when_a_starter_is_gone(
    players_operations, clubs_operations, lineups, squad
) -> None:
    lineups.replace(1, [34, 31, 30, 33, 32])
    clubs_operations.set_formation(1, "2-1-1")
    lineups.remove_player(34)

    details = build_use_case(players_operations, clubs_operations, lineups).execute(1)

    assert details.formation == "2-1-1"
    assert [view.id for view in details.players] == [30, 32, 31, 33]
    assert details.complete is False


def test_get_lineup_does_not_show_players_of_other_clubs(
    players_operations, clubs_operations, lineups, squad
) -> None:
    clubs_operations.formations[2] = None
    lineups.replace(2, [34])

    details = build_use_case(players_operations, clubs_operations, lineups).execute(1)

    assert details.players == []


def test_get_lineup_raises_not_found_for_unknown_club(
    players_operations, clubs_operations, lineups
) -> None:
    with pytest.raises(ClubNotFound):
        build_use_case(players_operations, clubs_operations, lineups).execute(99)
