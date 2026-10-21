from dataclasses import replace
from datetime import datetime

import pytest

from app.modules.league.application.get_match import GetMatch
from app.modules.league.domain.duels import Duel, DuelPlayer
from app.modules.league.domain.errors import MatchNotFound
from app.modules.league.domain.match import Match
from app.modules.players.domain.enums import PhysicalCondition, Position
from app.shared.domain.brasilia_time import BRASILIA


def a_duel(order: int) -> Duel:
    player = DuelPlayer(1, "Ana Lima", Position.ATA, PhysicalCondition.APTO, "shooting", 75)
    return Duel(order, 1, player, replace(player, attribute="defending"), goal=True)


def a_match() -> Match:
    return Match(
        id=None,
        home_club_id=1,
        away_club_id=2,
        home_goals=1,
        away_goals=0,
        home_formation="2-1-1",
        away_formation="3-1",
        played_at=datetime(2026, 11, 12, 15, 0, tzinfo=BRASILIA),
        duels=tuple(a_duel(order) for order in range(1, 7)),
    )


def test_get_match_returns_the_match_with_the_duels_and_the_club_names(
    clubs_operations, matches
) -> None:
    clubs_operations.add_club(2, "Delta FC")
    saved = matches.add(a_match())

    view = GetMatch(clubs_operations, matches).execute(saved.id)

    assert view.match == saved
    assert (view.home_club_name, view.away_club_name) == ("Águias FC", "Delta FC")
    assert [duel.order for duel in view.match.duels] == [1, 2, 3, 4, 5, 6]


def test_get_match_raises_not_found_for_an_unknown_match(clubs_operations, matches) -> None:
    with pytest.raises(MatchNotFound):
        GetMatch(clubs_operations, matches).execute(99)
