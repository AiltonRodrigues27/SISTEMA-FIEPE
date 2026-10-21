from dataclasses import replace
from datetime import datetime, timedelta

import pytest

from app.modules.clubs.domain.errors import ClubNotFound
from app.modules.league.application.list_matches import ListMatches
from app.modules.league.domain.match import Match
from app.shared.domain.brasilia_time import BRASILIA

FIRST = datetime(2026, 11, 12, 15, 0, tzinfo=BRASILIA)


def a_match(home: int, away: int, played_at: datetime) -> Match:
    return Match(
        id=None,
        home_club_id=home,
        away_club_id=away,
        home_goals=1,
        away_goals=0,
        home_formation="2-1-1",
        away_formation="2-1-1",
        played_at=played_at,
        duels=(),
    )


@pytest.fixture
def three_clubs(clubs_operations):
    clubs_operations.add_club(2, "Delta FC")
    clubs_operations.add_club(3, "Gama SC")


def test_list_matches_returns_the_most_recent_first(clubs_operations, matches, three_clubs) -> None:
    matches.add(a_match(1, 2, FIRST))
    matches.add(a_match(2, 3, FIRST + timedelta(days=2)))
    matches.add(a_match(3, 1, FIRST + timedelta(days=1)))

    views = ListMatches(clubs_operations, matches).execute(None)

    assert [view.match.id for view in views] == [2, 3, 1]


def test_list_matches_breaks_a_tie_in_the_time_with_the_greater_id(
    clubs_operations, matches, three_clubs
) -> None:
    matches.add(a_match(1, 2, FIRST))
    matches.add(a_match(2, 3, FIRST))
    matches.add(a_match(3, 1, FIRST))

    views = ListMatches(clubs_operations, matches).execute(None)

    assert [view.match.id for view in views] == [3, 2, 1]


def test_list_matches_filters_by_a_club_that_was_home_or_away(
    clubs_operations, matches, three_clubs
) -> None:
    matches.add(a_match(1, 2, FIRST))
    matches.add(a_match(2, 3, FIRST + timedelta(days=1)))
    matches.add(a_match(3, 1, FIRST + timedelta(days=2)))

    views = ListMatches(clubs_operations, matches).execute(1)

    assert [view.match.id for view in views] == [3, 1]


def test_list_matches_carries_the_club_names_and_no_duels(
    clubs_operations, matches, three_clubs
) -> None:
    matches.add(replace(a_match(1, 2, FIRST), duels=()))

    view = ListMatches(clubs_operations, matches).execute(None)[0]

    assert (view.home_club_name, view.away_club_name) == ("Águias FC", "Delta FC")
    assert view.match.duels == ()


def test_list_matches_without_matches_is_empty(clubs_operations, matches) -> None:
    assert ListMatches(clubs_operations, matches).execute(None) == []


def test_list_matches_of_a_club_that_never_played_is_empty(
    clubs_operations, matches, three_clubs
) -> None:
    matches.add(a_match(2, 3, FIRST))

    assert ListMatches(clubs_operations, matches).execute(1) == []


def test_list_matches_raises_not_found_for_an_unknown_club(clubs_operations, matches) -> None:
    with pytest.raises(ClubNotFound):
        ListMatches(clubs_operations, matches).execute(99)
