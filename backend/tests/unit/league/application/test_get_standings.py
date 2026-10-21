from datetime import datetime

from app.modules.league.application.get_standings import GetStandings
from app.modules.league.domain.match import Match
from app.shared.domain.brasilia_time import BRASILIA


def a_match(home: int, away: int, home_goals: int, away_goals: int) -> Match:
    return Match(
        id=None,
        home_club_id=home,
        away_club_id=away,
        home_goals=home_goals,
        away_goals=away_goals,
        home_formation="2-1-1",
        away_formation="2-1-1",
        played_at=datetime(2026, 11, 12, 15, 0, tzinfo=BRASILIA),
        duels=(),
    )


def test_get_standings_lists_every_club_even_before_the_first_match(
    clubs_operations, matches
) -> None:
    clubs_operations.add_club(2, "Delta FC")

    rows = GetStandings(clubs_operations, matches).execute()

    assert [(row.position, row.club_name, row.points) for row in rows] == [
        (1, "Águias FC", 0),
        (2, "Delta FC", 0),
    ]


def test_get_standings_builds_the_table_from_the_saved_matches(clubs_operations, matches) -> None:
    clubs_operations.add_club(2, "Delta FC")
    clubs_operations.add_club(3, "Gama SC")
    matches.add(a_match(1, 2, 1, 2))
    matches.add(a_match(3, 1, 0, 0))

    rows = GetStandings(clubs_operations, matches).execute()

    assert [(row.club_name, row.points, row.goal_difference) for row in rows] == [
        ("Delta FC", 3, 1),
        ("Gama SC", 1, 0),
        ("Águias FC", 1, -1),
    ]
