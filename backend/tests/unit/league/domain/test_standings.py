from datetime import datetime

from app.modules.league.domain.match import Match
from app.modules.league.domain.standings import calculate_standings
from app.shared.domain.brasilia_time import BRASILIA

PLAYED_AT = datetime(2026, 11, 12, 15, 0, tzinfo=BRASILIA)
EAGLES, DELTA, GAMA, EPSILON, MANGUE, TUBAROES = 1, 2, 3, 4, 5, 6
CLUB_NAMES = {
    EAGLES: "Águias FC",
    DELTA: "Delta FC",
    GAMA: "Gama SC",
    EPSILON: "Épsilon EC",
    MANGUE: "Mangue FC",
    TUBAROES: "Tubarões EC",
}


def scored(home: int, away: int, home_goals: int, away_goals: int) -> Match:
    return Match(
        id=None,
        home_club_id=home,
        away_club_id=away,
        home_goals=home_goals,
        away_goals=away_goals,
        home_formation="2-1-1",
        away_formation="2-1-1",
        played_at=PLAYED_AT,
        duels=(),
    )


def names_in_order(rows) -> list[str]:
    return [row.club_name for row in rows]


def test_standings_follow_the_example_of_the_statement() -> None:
    matches = [
        scored(EAGLES, DELTA, 1, 2),
        scored(GAMA, EPSILON, 2, 1),
        scored(EPSILON, EAGLES, 3, 2),
        scored(DELTA, GAMA, 0, 1),
    ]

    rows = calculate_standings(CLUB_NAMES, matches)

    assert [
        (row.position, row.club_name, row.points, row.goal_difference, row.goals_for)
        for row in rows
    ] == [
        (1, "Gama SC", 6, 2, 3),
        (2, "Épsilon EC", 3, 0, 4),
        (3, "Delta FC", 3, 0, 2),
        (4, "Mangue FC", 0, 0, 0),
        (5, "Tubarões EC", 0, 0, 0),
        (6, "Águias FC", 0, -2, 3),
    ]


def test_each_row_counts_games_wins_draws_losses_and_goals() -> None:
    matches = [scored(EAGLES, DELTA, 1, 2), scored(DELTA, EAGLES, 1, 1)]

    rows = {row.club_id: row for row in calculate_standings(CLUB_NAMES, matches)}

    delta = rows[DELTA]
    assert (delta.played, delta.wins, delta.draws, delta.losses) == (2, 1, 1, 0)
    assert (delta.goals_for, delta.goals_against, delta.goal_difference) == (3, 2, 1)
    assert delta.points == 4
    eagles = rows[EAGLES]
    assert (eagles.played, eagles.wins, eagles.draws, eagles.losses) == (2, 0, 1, 1)
    assert eagles.points == 1


def test_a_draw_gives_one_point_to_each_club() -> None:
    rows = {
        row.club_id: row for row in calculate_standings(CLUB_NAMES, [scored(GAMA, DELTA, 2, 2)])
    }

    assert (rows[GAMA].points, rows[DELTA].points) == (1, 1)


def test_clubs_that_never_played_appear_with_zeros_in_name_order() -> None:
    rows = calculate_standings(CLUB_NAMES, [])

    assert names_in_order(rows) == [
        "Águias FC",
        "Delta FC",
        "Épsilon EC",
        "Gama SC",
        "Mangue FC",
        "Tubarões EC",
    ]
    assert all(row.played == 0 and row.points == 0 for row in rows)


def test_positions_run_from_one_to_the_number_of_clubs_without_repeating() -> None:
    rows = calculate_standings(CLUB_NAMES, [scored(GAMA, DELTA, 2, 0)])

    assert [row.position for row in rows] == [1, 2, 3, 4, 5, 6]


def test_more_points_come_before_a_better_goal_difference() -> None:
    names = {1: "Xis FC", 2: "Yago FC", 3: "Pedra FC", 4: "Quina FC"}
    matches = [
        scored(1, 3, 1, 0),
        scored(4, 1, 5, 0),
        scored(2, 3, 0, 0),
        scored(2, 4, 0, 0),
    ]

    rows = calculate_standings(names, matches)

    assert names_in_order(rows) == ["Quina FC", "Xis FC", "Yago FC", "Pedra FC"]
    assert [row.goal_difference for row in rows] == [5, -4, 0, -1]


def test_the_goal_difference_breaks_a_tie_in_points() -> None:
    matches = [scored(EAGLES, MANGUE, 1, 0), scored(DELTA, TUBAROES, 3, 0)]

    rows = calculate_standings(CLUB_NAMES, matches)

    assert names_in_order(rows)[:2] == ["Delta FC", "Águias FC"]


def test_goals_scored_break_a_tie_in_points_and_goal_difference() -> None:
    matches = [scored(DELTA, MANGUE, 2, 1), scored(EAGLES, TUBAROES, 1, 0)]

    rows = calculate_standings(CLUB_NAMES, matches)

    assert names_in_order(rows)[:2] == ["Delta FC", "Águias FC"]


def test_the_name_ignores_case_and_accents_when_it_breaks_a_tie() -> None:
    rows = calculate_standings({1: "Zeta FC", 2: "épsilon EC", 3: "Delta FC"}, [])

    assert names_in_order(rows) == ["Delta FC", "épsilon EC", "Zeta FC"]


def test_names_that_are_equal_without_accents_are_tied_by_the_smaller_id() -> None:
    rows = calculate_standings({7: "Águias FC", 3: "Aguias FC"}, [])

    assert [row.club_id for row in rows] == [3, 7]
