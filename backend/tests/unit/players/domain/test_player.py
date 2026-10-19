from dataclasses import replace
from decimal import Decimal

import pytest

from app.modules.players.domain.entities import Attributes, Player, PlayerRegistration
from app.modules.players.domain.enums import PhysicalCondition, Position
from app.modules.players.domain.errors import (
    AgeCannotDecrease,
    InvalidConditionTransition,
    InvalidPlayerData,
    PlayerHasClub,
    PlayerIsFree,
    PlayerNotFree,
    PositionChangeNotAllowed,
)

APTO = PhysicalCondition.APTO
MAL = PhysicalCondition.MAL_CONDICIONADO
DOENTE = PhysicalCondition.DOENTE

VALID_REGISTRATION = PlayerRegistration(
    name="Vini Jr",
    position=Position.MEI,
    agility=85,
    age=25,
    attributes=Attributes(70, 68, 82, 79, 55, 64),
    potential=86,
)

VETERAN_REGISTRATION = PlayerRegistration(
    name="Cristiano Ronaldo",
    position=Position.ATA,
    agility=85,
    age=41,
    attributes=Attributes(
        pace=70, shooting=95, passing=82, dribbling=85, defending=55, physical=90
    ),
    potential=95,
)


def build_player(club_id: int | None = None) -> Player:
    player = Player.register(VALID_REGISTRATION)
    player.club_id = club_id
    return player


def test_register_creates_free_apto_player_with_base_value() -> None:
    player = Player.register(VALID_REGISTRATION)

    assert player.id is None
    assert player.condition is APTO
    assert player.is_free
    assert player.base_value == Decimal("40.00")


@pytest.mark.parametrize(
    "changes",
    [
        {"age": 35, "agility": 86},
        {"attributes": Attributes(80, 80, 80, 80, 80, 81), "potential": 90},
        {"potential": 81},
        {"age": 33, "potential": 90},
    ],
    ids=[
        "agility_above_85_from_35",
        "attributes_sum_above_480",
        "potential_below_highest_attribute",
        "potential_not_equal_to_highest_from_33",
    ],
)
def test_register_rejects_inconsistent_data(changes: dict[str, object]) -> None:
    with pytest.raises(InvalidPlayerData):
        Player.register(replace(VALID_REGISTRATION, **changes))


@pytest.mark.parametrize(
    "changes",
    [
        {"age": 35, "agility": 85, "potential": 82},
        {"attributes": Attributes(80, 80, 80, 80, 80, 80), "potential": 80},
        {"age": 33, "potential": 82},
    ],
    ids=[
        "agility_85_at_35",
        "attributes_sum_exactly_480",
        "potential_equal_to_highest_at_33",
    ],
)
def test_register_accepts_limit_values(changes: dict[str, object]) -> None:
    player = Player.register(replace(VALID_REGISTRATION, **changes))

    assert player.condition is APTO


def test_register_accepts_veteran_with_potential_equal_to_highest_attribute() -> None:
    player = Player.register(VETERAN_REGISTRATION)

    assert player.base_value == Decimal("106.00")


@pytest.mark.parametrize(
    "changes",
    [{"agility": 90}, {"potential": 90}],
    ids=["agility_above_85_at_41", "potential_below_highest_attribute_at_41"],
)
def test_register_rejects_veteran_with_invalid_agility_or_potential(
    changes: dict[str, object],
) -> None:
    with pytest.raises(InvalidPlayerData):
        Player.register(replace(VETERAN_REGISTRATION, **changes))


def test_update_profile_changes_the_four_editable_fields() -> None:
    player = build_player()

    player.update_profile("Neymar Jr", Position.ATA, 70, 26)

    assert (player.name, player.position, player.agility, player.age) == (
        "Neymar Jr",
        Position.ATA,
        70,
        26,
    )


def test_update_profile_rejects_position_change_when_player_has_club() -> None:
    player = build_player(club_id=1)

    with pytest.raises(PositionChangeNotAllowed):
        player.update_profile("Neymar Jr", Position.ATA, 80, 26)

    assert player.position is Position.MEI
    assert player.name == "Vini Jr"


def test_update_profile_allows_same_position_when_player_has_club() -> None:
    player = build_player(club_id=1)

    player.update_profile("Neymar Jr", Position.MEI, 80, 26)

    assert player.name == "Neymar Jr"


def test_update_profile_rejects_age_decrease() -> None:
    player = build_player()

    with pytest.raises(AgeCannotDecrease):
        player.update_profile(player.name, player.position, player.agility, 24)

    assert player.age == 25


def test_update_profile_accepts_same_age() -> None:
    player = build_player()

    player.update_profile(player.name, player.position, player.agility, 25)

    assert player.age == 25


def test_update_profile_rejects_agility_above_85_from_35() -> None:
    player = build_player()

    with pytest.raises(InvalidPlayerData):
        player.update_profile(player.name, player.position, 86, 35)

    assert player.age == 25


@pytest.mark.parametrize(
    ("current", "new"),
    [
        (APTO, MAL),
        (APTO, DOENTE),
        (MAL, APTO),
        (MAL, DOENTE),
        (DOENTE, MAL),
        (APTO, APTO),
        (DOENTE, DOENTE),
    ],
)
def test_change_condition_accepts_allowed_transitions(
    current: PhysicalCondition, new: PhysicalCondition
) -> None:
    player = build_player()
    player.condition = current

    player.change_condition(new)

    assert player.condition is new


def test_change_condition_rejects_doente_to_apto() -> None:
    player = build_player()
    player.condition = DOENTE

    with pytest.raises(InvalidConditionTransition):
        player.change_condition(APTO)

    assert player.condition is DOENTE


def test_assign_to_sets_club_when_player_is_free() -> None:
    player = build_player()

    player.assign_to(7)

    assert player.club_id == 7


def test_assign_to_rejects_player_that_already_has_club() -> None:
    player = build_player(club_id=1)

    with pytest.raises(PlayerNotFree):
        player.assign_to(2)

    assert player.club_id == 1


def test_release_returns_previous_club_and_frees_player() -> None:
    player = build_player(club_id=3)

    previous_club_id = player.release()

    assert previous_club_id == 3
    assert player.is_free


def test_release_rejects_free_player() -> None:
    with pytest.raises(PlayerIsFree):
        build_player().release()


def test_ensure_can_be_deleted_accepts_free_player() -> None:
    build_player().ensure_can_be_deleted()


def test_ensure_can_be_deleted_rejects_player_with_club() -> None:
    with pytest.raises(PlayerHasClub):
        build_player(club_id=1).ensure_can_be_deleted()


def test_overall_is_calculated_from_position_and_attributes() -> None:
    assert build_player().overall == 75


def test_market_value_follows_the_current_condition() -> None:
    player = build_player()

    assert player.market_value == Decimal("40.00")

    player.change_condition(MAL)

    assert player.market_value == Decimal("37.00")
