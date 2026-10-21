from datetime import timedelta

import pytest

from app.modules.clubs.domain.errors import ClubNotFound
from app.modules.league.application.get_lineup import GetLineup
from app.modules.league.application.play_match import PlayMatch
from app.modules.league.domain.errors import LineupIncomplete, SameClubMatch
from app.modules.league.domain.match import MatchResult
from app.modules.players.domain.entities import Attributes
from app.modules.players.domain.enums import PhysicalCondition, Position

APTO = PhysicalCondition.APTO
MAL = PhysicalCondition.MAL_CONDICIONADO
# Attributes(pace, shooting, passing, dribbling, defending, physical)
EAGLES = [
    (30, "Rui Prado", Position.GOL, APTO, Attributes(1, 1, 1, 1, 77, 1)),
    (32, "Téo Brandão", Position.ZAG, APTO, Attributes(1, 1, 1, 1, 84, 1)),
    (31, "Davi Lins", Position.LAT, MAL, Attributes(1, 1, 1, 74, 66, 1)),
    (33, "Lauro Neves", Position.MEI, APTO, Attributes(1, 1, 82, 1, 1, 1)),
    (34, "Otto Rangel", Position.ATA, APTO, Attributes(1, 75, 1, 1, 1, 1)),
]
DELTA = [
    (40, "Ivo Teles", Position.GOL, APTO, Attributes(1, 1, 1, 1, 72, 1)),
    (41, "Hugo Vaz", Position.ZAG, APTO, Attributes(1, 1, 1, 1, 84, 1)),
    (42, "Lino Matos", Position.LAT, APTO, Attributes(1, 1, 1, 79, 63, 1)),
    (43, "Nei Soares", Position.MEI, APTO, Attributes(1, 1, 70, 1, 1, 1)),
    (44, "Ugo Falcão", Position.ATA, APTO, Attributes(1, 81, 1, 1, 1, 1)),
]


@pytest.fixture
def ready_clubs(give_lineup):
    give_lineup(1, "Águias FC", "2-1-1", EAGLES)
    give_lineup(2, "Delta FC", "2-1-1", DELTA)


def build_use_case(players_operations, clubs_operations, lineups, matches, clock, unit_of_work):
    get_lineup = GetLineup(players_operations, clubs_operations, lineups)
    return PlayMatch(get_lineup, clubs_operations, matches, clock, unit_of_work)


def assert_nothing_was_written(matches, unit_of_work):
    assert matches.stored == []
    assert unit_of_work.commits == 0


def test_play_match_follows_the_example_of_the_statement(
    players_operations, clubs_operations, lineups, matches, clock, unit_of_work, ready_clubs
) -> None:
    use_case = build_use_case(
        players_operations, clubs_operations, lineups, matches, clock, unit_of_work
    )

    view = use_case.execute(1, 2)

    match = view.match
    assert match.id == 1
    assert (view.home_club_name, view.away_club_name) == ("Águias FC", "Delta FC")
    assert (match.home_goals, match.away_goals) == (1, 2)
    assert match.result is MatchResult.VISITANTE
    assert [duel.goal for duel in match.duels] == [True, False, False, True, False, True]


def test_play_match_saves_the_match_with_the_clock_time_and_commits_once(
    players_operations, clubs_operations, lineups, matches, clock, unit_of_work, ready_clubs
) -> None:
    use_case = build_use_case(
        players_operations, clubs_operations, lineups, matches, clock, unit_of_work
    )

    use_case.execute(1, 2)

    assert len(matches.stored) == 1
    saved = matches.stored[0]
    assert saved.played_at == clock.moment
    assert (saved.home_formation, saved.away_formation) == ("2-1-1", "2-1-1")
    assert len(saved.duels) == 6
    assert unit_of_work.commits == 1


def test_play_match_does_not_change_the_lineups_or_the_formations(
    players_operations, clubs_operations, lineups, matches, clock, unit_of_work, ready_clubs
) -> None:
    lineups_before = {club_id: list(ids) for club_id, ids in lineups.stored.items()}
    formations_before = dict(clubs_operations.formations)
    use_case = build_use_case(
        players_operations, clubs_operations, lineups, matches, clock, unit_of_work
    )

    use_case.execute(1, 2)

    assert lineups.stored == lineups_before
    assert clubs_operations.formations == formations_before


def test_the_same_confrontation_can_be_played_again(
    players_operations, clubs_operations, lineups, matches, clock, unit_of_work, ready_clubs
) -> None:
    use_case = build_use_case(
        players_operations, clubs_operations, lineups, matches, clock, unit_of_work
    )

    first = use_case.execute(1, 2)
    clock.moment += timedelta(minutes=5)
    second = use_case.execute(1, 2)

    assert (first.match.id, second.match.id) == (1, 2)
    assert first.match.duels == second.match.duels
    assert unit_of_work.commits == 2


def test_play_match_rejects_the_same_club_as_home_and_away(
    players_operations, clubs_operations, lineups, matches, clock, unit_of_work, ready_clubs
) -> None:
    use_case = build_use_case(
        players_operations, clubs_operations, lineups, matches, clock, unit_of_work
    )

    with pytest.raises(SameClubMatch):
        use_case.execute(1, 1)

    assert_nothing_was_written(matches, unit_of_work)


def test_play_match_checks_the_same_club_before_looking_for_it(
    players_operations, clubs_operations, lineups, matches, clock, unit_of_work
) -> None:
    use_case = build_use_case(
        players_operations, clubs_operations, lineups, matches, clock, unit_of_work
    )

    with pytest.raises(SameClubMatch):
        use_case.execute(999, 999)


@pytest.mark.parametrize(("home", "away"), [(99, 2), (1, 99)])
def test_play_match_raises_not_found_for_an_unknown_club(
    players_operations,
    clubs_operations,
    lineups,
    matches,
    clock,
    unit_of_work,
    ready_clubs,
    home,
    away,
) -> None:
    use_case = build_use_case(
        players_operations, clubs_operations, lineups, matches, clock, unit_of_work
    )

    with pytest.raises(ClubNotFound):
        use_case.execute(home, away)

    assert_nothing_was_written(matches, unit_of_work)


@pytest.mark.parametrize(("home", "away"), [(1, 2), (2, 1)])
def test_play_match_rejects_a_club_that_lost_a_starter(
    players_operations,
    clubs_operations,
    lineups,
    matches,
    clock,
    unit_of_work,
    ready_clubs,
    home,
    away,
) -> None:
    lineups.remove_player(34)
    use_case = build_use_case(
        players_operations, clubs_operations, lineups, matches, clock, unit_of_work
    )

    with pytest.raises(LineupIncomplete):
        use_case.execute(home, away)

    assert_nothing_was_written(matches, unit_of_work)


def test_play_match_rejects_a_club_that_never_made_a_lineup(
    players_operations, clubs_operations, lineups, matches, clock, unit_of_work, give_lineup
) -> None:
    give_lineup(1, "Águias FC", "2-1-1", EAGLES)
    clubs_operations.add_club(2, "Delta FC")
    use_case = build_use_case(
        players_operations, clubs_operations, lineups, matches, clock, unit_of_work
    )

    with pytest.raises(LineupIncomplete):
        use_case.execute(1, 2)

    assert_nothing_was_written(matches, unit_of_work)


def test_play_match_reports_an_unknown_club_before_an_incomplete_lineup(
    players_operations, clubs_operations, lineups, matches, clock, unit_of_work, ready_clubs
) -> None:
    lineups.remove_player(34)
    use_case = build_use_case(
        players_operations, clubs_operations, lineups, matches, clock, unit_of_work
    )

    with pytest.raises(ClubNotFound):
        use_case.execute(1, 99)
