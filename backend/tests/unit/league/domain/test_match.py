from dataclasses import replace
from datetime import datetime

import pytest

from app.modules.league.domain.match import Match, MatchResult
from app.shared.domain.brasilia_time import BRASILIA

PLAYED_AT = datetime(2026, 11, 12, 15, 0, tzinfo=BRASILIA)


def scored(home_goals: int, away_goals: int) -> Match:
    return Match(
        id=None,
        home_club_id=1,
        away_club_id=2,
        home_goals=home_goals,
        away_goals=away_goals,
        home_formation="2-1-1",
        away_formation="2-1-1",
        played_at=PLAYED_AT,
        duels=(),
    )


def test_play_follows_the_example_of_the_statement(eagles, delta) -> None:
    match = Match.play(eagles, delta, PLAYED_AT)

    assert match.id is None
    assert (match.home_club_id, match.away_club_id) == (1, 2)
    assert (match.home_goals, match.away_goals) == (1, 2)
    assert (match.home_formation, match.away_formation) == ("2-1-1", "2-1-1")
    assert match.played_at == PLAYED_AT
    assert match.result is MatchResult.VISITANTE
    assert len(match.duels) == 6


def test_play_keeps_the_formation_of_each_team(eagles, delta) -> None:
    away = replace(delta, formation="1-2-1")

    match = Match.play(eagles, away, PLAYED_AT)

    assert (match.home_formation, match.away_formation) == ("2-1-1", "1-2-1")


@pytest.mark.parametrize(
    ("home_goals", "away_goals", "expected"),
    [
        pytest.param(3, 0, MatchResult.MANDANTE, id="home_wins_by_three"),
        pytest.param(2, 1, MatchResult.MANDANTE, id="home_wins_by_one"),
        pytest.param(0, 1, MatchResult.VISITANTE, id="away_wins_by_one"),
        pytest.param(1, 3, MatchResult.VISITANTE, id="away_wins_by_two"),
        pytest.param(0, 0, MatchResult.EMPATE, id="goalless_draw"),
        pytest.param(2, 2, MatchResult.EMPATE, id="scoring_draw"),
    ],
)
def test_result_comes_from_the_goals_of_each_club(home_goals, away_goals, expected) -> None:
    assert scored(home_goals, away_goals).result is expected
