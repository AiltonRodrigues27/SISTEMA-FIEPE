import pytest
from pydantic import ValidationError

from app.modules.league.adapters.inbound.http.schemas import SetLineupRequest

VALID_IDS = [34, 31, 30, 33, 32]


def parse(**fields):
    return SetLineupRequest.model_validate(
        {"formation": "2-1-1", "player_ids": VALID_IDS, **fields}
    )


@pytest.mark.parametrize("formation", ["3-1", "2-2", "2-1-1", "1-2-1"])
def test_every_known_formation_is_accepted(formation) -> None:
    assert parse(formation=formation).formation == formation


def test_valid_body_keeps_the_ids_in_the_order_received() -> None:
    assert parse().player_ids == VALID_IDS


def test_ids_sent_as_whole_decimals_are_accepted() -> None:
    assert parse(player_ids=[34.0, 31, 30, 33, 32]).player_ids == VALID_IDS


@pytest.mark.parametrize(
    "formation",
    [
        pytest.param("4-4-2", id="unknown_formation"),
        pytest.param("2-1-1 ", id="trailing_space"),
        pytest.param("", id="empty"),
        pytest.param("211", id="without_dashes"),
        pytest.param("2-1-1-0", id="too_many_sectors"),
        pytest.param(211, id="number"),
        pytest.param(None, id="null"),
        pytest.param(["2-1-1"], id="list"),
    ],
)
def test_formation_outside_the_list_is_rejected(formation) -> None:
    with pytest.raises(ValidationError):
        parse(formation=formation)


@pytest.mark.parametrize(
    "player_ids",
    [
        pytest.param([34, 31, 30, 33], id="four_ids"),
        pytest.param([34, 31, 30, 33, 32, 35], id="six_ids"),
        pytest.param([], id="empty_list"),
        pytest.param([34, 34, 30, 33, 32], id="repeated_id"),
        pytest.param([34, 31, 30, 33, 0], id="zero"),
        pytest.param([34, 31, 30, 33, -1], id="negative"),
        pytest.param([34, 31, 30, 33, "32"], id="text_id"),
        pytest.param([34, 31, 30, 33, 32.5], id="fractional_id"),
        pytest.param([34, 31, 30, 33, True], id="boolean_id"),
        pytest.param([34, 31, 30, 33, None], id="null_id"),
        pytest.param([34, 31, 30, 33, 2147483648], id="id_above_int32"),
        pytest.param("34,31,30,33,32", id="text"),
        pytest.param({"0": 34}, id="object"),
        pytest.param(None, id="null"),
    ],
)
def test_player_ids_outside_the_rules_are_rejected(player_ids) -> None:
    with pytest.raises(ValidationError):
        parse(player_ids=player_ids)


@pytest.mark.parametrize("missing", ["formation", "player_ids"])
def test_missing_field_is_rejected(missing) -> None:
    body = {"formation": "2-1-1", "player_ids": VALID_IDS}
    del body[missing]

    with pytest.raises(ValidationError):
        SetLineupRequest.model_validate(body)


def test_other_fields_are_ignored() -> None:
    request = parse(cash=999, club_id=7, complete=True)

    assert not hasattr(request, "cash")
    assert request.formation == "2-1-1"
