from dataclasses import replace

import pytest

from app.modules.clubs.domain.errors import ClubNotFound
from app.modules.league.application.set_lineup import SetLineup
from app.modules.league.domain.errors import (
    PlayerNotInSquad,
    PlayerUnavailable,
    PositionsDoNotFormFormation,
)
from app.modules.players.domain.enums import PhysicalCondition, Position
from app.modules.players.domain.errors import PlayerNotFound

STARTERS_2_1_1 = [34, 31, 30, 33, 32]


def build_use_case(players_operations, clubs_operations, lineups, unit_of_work) -> SetLineup:
    return SetLineup(players_operations, clubs_operations, lineups, unit_of_work)


def assert_nothing_was_written(lineups, clubs_operations, unit_of_work, previous_formation=None):
    assert lineups.stored == {}
    assert clubs_operations.formations[1] == previous_formation
    assert unit_of_work.commits == 0


def test_set_lineup_saves_the_starters_and_the_formation_and_commits_once(
    players_operations, clubs_operations, lineups, unit_of_work, squad
) -> None:
    use_case = build_use_case(players_operations, clubs_operations, lineups, unit_of_work)

    details = use_case.execute(1, "2-1-1", STARTERS_2_1_1)

    assert sorted(lineups.stored[1]) == [30, 31, 32, 33, 34]
    assert clubs_operations.formations[1] == "2-1-1"
    assert unit_of_work.commits == 1
    assert (details.club_id, details.formation, details.complete) == (1, "2-1-1", True)


def test_set_lineup_returns_the_starters_in_squad_order(
    players_operations, clubs_operations, lineups, unit_of_work, squad
) -> None:
    use_case = build_use_case(players_operations, clubs_operations, lineups, unit_of_work)

    details = use_case.execute(1, "2-1-1", STARTERS_2_1_1)

    assert [view.name for view in details.players] == [
        "Rui Prado",
        "Teo Brandao",
        "Davi Lins",
        "Lauro Neves",
        "Otto Rangel",
    ]


def test_set_lineup_replaces_the_previous_lineup_as_a_whole(
    players_operations, clubs_operations, lineups, unit_of_work, squad
) -> None:
    use_case = build_use_case(players_operations, clubs_operations, lineups, unit_of_work)
    use_case.execute(1, "2-1-1", STARTERS_2_1_1)

    details = use_case.execute(1, "2-2", [30, 31, 32, 34, 35])

    assert sorted(lineups.stored[1]) == [30, 31, 32, 34, 35]
    assert details.formation == "2-2"
    assert 33 not in [view.id for view in details.players]


def test_set_lineup_accepts_a_mal_condicionado_player(
    players_operations, clubs_operations, lineups, unit_of_work, squad
) -> None:
    players_operations.views[31] = replace(
        players_operations.views[31], condition=PhysicalCondition.MAL_CONDICIONADO
    )
    use_case = build_use_case(players_operations, clubs_operations, lineups, unit_of_work)

    details = use_case.execute(1, "2-1-1", STARTERS_2_1_1)

    assert details.complete is True


def test_set_lineup_raises_not_found_for_unknown_club(
    players_operations, clubs_operations, lineups, unit_of_work, squad
) -> None:
    use_case = build_use_case(players_operations, clubs_operations, lineups, unit_of_work)

    with pytest.raises(ClubNotFound):
        use_case.execute(99, "2-1-1", STARTERS_2_1_1)

    assert lineups.stored == {}
    assert unit_of_work.commits == 0


def test_set_lineup_raises_not_found_for_unknown_player(
    players_operations, clubs_operations, lineups, unit_of_work, squad
) -> None:
    use_case = build_use_case(players_operations, clubs_operations, lineups, unit_of_work)

    with pytest.raises(PlayerNotFound):
        use_case.execute(1, "2-1-1", [34, 31, 30, 33, 999])

    assert_nothing_was_written(lineups, clubs_operations, unit_of_work)


def test_set_lineup_rejects_a_player_from_another_club(
    players_operations, clubs_operations, lineups, unit_of_work, squad, add_player
) -> None:
    add_player(40, "Ivo Teles", Position.ATA, club_id=2)
    use_case = build_use_case(players_operations, clubs_operations, lineups, unit_of_work)

    with pytest.raises(PlayerNotInSquad):
        use_case.execute(1, "2-1-1", [40, 31, 30, 33, 32])

    assert_nothing_was_written(lineups, clubs_operations, unit_of_work)


def test_set_lineup_rejects_a_free_player(
    players_operations, clubs_operations, lineups, unit_of_work, squad, add_player
) -> None:
    add_player(40, "Ivo Teles", Position.ATA, club_id=None)
    use_case = build_use_case(players_operations, clubs_operations, lineups, unit_of_work)

    with pytest.raises(PlayerNotInSquad):
        use_case.execute(1, "2-1-1", [40, 31, 30, 33, 32])

    assert_nothing_was_written(lineups, clubs_operations, unit_of_work)


def test_set_lineup_rejects_a_sick_player(
    players_operations, clubs_operations, lineups, unit_of_work, squad, add_player
) -> None:
    add_player(40, "Ivo Teles", Position.ATA, condition=PhysicalCondition.DOENTE)
    use_case = build_use_case(players_operations, clubs_operations, lineups, unit_of_work)

    with pytest.raises(PlayerUnavailable):
        use_case.execute(1, "2-1-1", [40, 31, 30, 33, 32])

    assert_nothing_was_written(lineups, clubs_operations, unit_of_work)


def test_set_lineup_rejects_positions_that_do_not_fill_the_formation(
    players_operations, clubs_operations, lineups, unit_of_work, squad
) -> None:
    use_case = build_use_case(players_operations, clubs_operations, lineups, unit_of_work)

    with pytest.raises(PositionsDoNotFormFormation):
        use_case.execute(1, "3-1", STARTERS_2_1_1)

    assert_nothing_was_written(lineups, clubs_operations, unit_of_work)


def test_set_lineup_keeps_the_previous_lineup_when_the_new_one_is_refused(
    players_operations, clubs_operations, lineups, unit_of_work, squad
) -> None:
    use_case = build_use_case(players_operations, clubs_operations, lineups, unit_of_work)
    use_case.execute(1, "2-1-1", STARTERS_2_1_1)

    with pytest.raises(PositionsDoNotFormFormation):
        use_case.execute(1, "1-2-1", STARTERS_2_1_1)

    assert sorted(lineups.stored[1]) == [30, 31, 32, 33, 34]
    assert clubs_operations.formations[1] == "2-1-1"
    assert unit_of_work.commits == 1


def test_set_lineup_reports_an_unknown_player_before_a_rule_violation(
    players_operations, clubs_operations, lineups, unit_of_work, squad, add_player
) -> None:
    add_player(40, "Ivo Teles", Position.ATA, condition=PhysicalCondition.DOENTE)
    use_case = build_use_case(players_operations, clubs_operations, lineups, unit_of_work)

    with pytest.raises(PlayerNotFound):
        use_case.execute(1, "2-1-1", [40, 31, 30, 33, 999])
