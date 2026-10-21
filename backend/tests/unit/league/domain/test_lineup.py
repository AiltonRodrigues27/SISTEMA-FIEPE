import pytest

from app.modules.league.domain.errors import (
    PlayerNotInSquad,
    PlayerUnavailable,
    PositionsDoNotFormFormation,
)
from app.modules.league.domain.formations import FORMATIONS, LINEUP_SIZE
from app.modules.league.domain.lineup import LineupCandidate, ensure_valid_lineup
from app.modules.players.domain.enums import Position

GOL, ZAG, LAT, MEI, ATA = (
    Position.GOL,
    Position.ZAG,
    Position.LAT,
    Position.MEI,
    Position.ATA,
)
CLUB_ID = 1


def candidates_for(*positions: Position, club_id: int | None = CLUB_ID) -> list[LineupCandidate]:
    return [
        LineupCandidate(player_id=index, club_id=club_id, position=position, can_play=True)
        for index, position in enumerate(positions, start=1)
    ]


def test_every_formation_has_one_goalkeeper_and_four_field_players() -> None:
    for shape in FORMATIONS.values():
        assert shape.defense + shape.midfield + shape.attack == LINEUP_SIZE - 1


@pytest.mark.parametrize(
    ("formation", "positions"),
    [
        pytest.param("3-1", (GOL, ZAG, LAT, LAT, ATA), id="3-1_with_one_zag_and_two_lat"),
        pytest.param("3-1", (GOL, ZAG, ZAG, ZAG, ATA), id="3-1_with_three_zag"),
        pytest.param("2-2", (GOL, ZAG, LAT, ATA, ATA), id="2-2"),
        pytest.param("2-1-1", (GOL, ZAG, LAT, MEI, ATA), id="2-1-1"),
        pytest.param("2-1-1", (ATA, MEI, LAT, ZAG, GOL), id="2-1-1_in_any_order"),
        pytest.param("1-2-1", (GOL, ZAG, MEI, MEI, ATA), id="1-2-1_with_zag"),
        pytest.param("1-2-1", (GOL, LAT, MEI, MEI, ATA), id="1-2-1_with_lat"),
    ],
)
def test_positions_that_fill_the_formation_are_accepted(formation, positions) -> None:
    ensure_valid_lineup(CLUB_ID, formation, candidates_for(*positions))


@pytest.mark.parametrize(
    ("formation", "positions"),
    [
        pytest.param("2-1-1", (ZAG, LAT, MEI, ATA, ATA), id="no_goalkeeper"),
        pytest.param("2-1-1", (GOL, GOL, ZAG, MEI, ATA), id="two_goalkeepers"),
        pytest.param("2-1-1", (GOL, ZAG, MEI, MEI, ATA), id="one_defender_too_few"),
        pytest.param("2-1-1", (GOL, ZAG, LAT, LAT, ATA), id="midfielder_missing"),
        pytest.param("2-1-1", (GOL, ZAG, LAT, MEI, MEI), id="attacker_missing"),
        pytest.param("2-2", (GOL, ZAG, LAT, MEI, ATA), id="2-2_with_a_midfielder"),
        pytest.param("3-1", (GOL, ZAG, LAT, ATA, ATA), id="3-1_with_two_attackers"),
        pytest.param("1-2-1", (GOL, ZAG, LAT, MEI, ATA), id="1-2-1_with_two_defenders"),
    ],
)
def test_positions_that_do_not_fill_the_formation_are_rejected(formation, positions) -> None:
    with pytest.raises(PositionsDoNotFormFormation):
        ensure_valid_lineup(CLUB_ID, formation, candidates_for(*positions))


@pytest.mark.parametrize("other_club_id", [2, None])
def test_a_player_from_another_club_or_a_free_player_is_not_in_the_squad(other_club_id) -> None:
    candidates = candidates_for(GOL, ZAG, LAT, MEI, ATA)
    candidates[3] = LineupCandidate(player_id=4, club_id=other_club_id, position=MEI, can_play=True)

    with pytest.raises(PlayerNotInSquad):
        ensure_valid_lineup(CLUB_ID, "2-1-1", candidates)


def test_a_player_who_cannot_play_is_rejected() -> None:
    candidates = candidates_for(GOL, ZAG, LAT, MEI, ATA)
    candidates[2] = LineupCandidate(player_id=3, club_id=CLUB_ID, position=LAT, can_play=False)

    with pytest.raises(PlayerUnavailable):
        ensure_valid_lineup(CLUB_ID, "2-1-1", candidates)


def test_the_squad_check_comes_before_the_availability_check() -> None:
    candidates = candidates_for(GOL, ZAG, LAT, MEI, ATA)
    candidates[1] = LineupCandidate(player_id=2, club_id=CLUB_ID, position=ZAG, can_play=False)
    candidates[4] = LineupCandidate(player_id=5, club_id=2, position=ATA, can_play=True)

    with pytest.raises(PlayerNotInSquad):
        ensure_valid_lineup(CLUB_ID, "2-1-1", candidates)


def test_the_availability_check_comes_before_the_positions_check() -> None:
    candidates = candidates_for(GOL, GOL, LAT, MEI, ATA)
    candidates[2] = LineupCandidate(player_id=3, club_id=CLUB_ID, position=LAT, can_play=False)

    with pytest.raises(PlayerUnavailable):
        ensure_valid_lineup(CLUB_ID, "2-1-1", candidates)
