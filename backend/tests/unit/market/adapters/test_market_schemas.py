from datetime import datetime

import pytest
from pydantic import ValidationError

from app.modules.market.adapters.inbound.http.schemas import BuyPlayerRequest
from app.shared.domain.brasilia_time import BRASILIA

VALID = {"club_id": 1, "loyalty_until": "2027-03-02T10:15-03:00"}


def test_valid_body_is_parsed_with_the_brasilia_time_zone() -> None:
    request = BuyPlayerRequest.model_validate(VALID)

    assert request.club_id == 1
    assert request.loyalty_until == datetime(2027, 3, 2, 10, 15, tzinfo=BRASILIA)
    assert request.loyalty_until.utcoffset().total_seconds() == -3 * 3600


@pytest.mark.parametrize(
    "loyalty_until",
    [
        pytest.param("2027-03-02T10:15", id="without_the_offset"),
        pytest.param("2027-03-02T10:15:00-03:00", id="with_seconds"),
        pytest.param("2027-03-02T10:15+00:00", id="other_offset"),
        pytest.param("2027-03-02T10:15Z", id="utc_marker"),
        pytest.param("2027-03-02 10:15-03:00", id="space_instead_of_the_t"),
        pytest.param("2027-03-02", id="date_only"),
        pytest.param("02/03/2027 10:15", id="brazilian_format"),
        pytest.param("2027-02-30T10:15-03:00", id="day_that_does_not_exist"),
        pytest.param("2027-03-02T24:00-03:00", id="hour_that_does_not_exist"),
        pytest.param("2027-13-02T10:15-03:00", id="month_that_does_not_exist"),
        pytest.param("", id="empty"),
        pytest.param(None, id="null"),
        pytest.param(20270302, id="number"),
    ],
)
def test_loyalty_until_outside_the_format_is_rejected(loyalty_until) -> None:
    with pytest.raises(ValidationError):
        BuyPlayerRequest.model_validate({**VALID, "loyalty_until": loyalty_until})


@pytest.mark.parametrize(
    "club_id",
    [
        pytest.param(0, id="zero"),
        pytest.param(-1, id="negative"),
        pytest.param("1", id="text"),
        pytest.param(1.5, id="fraction"),
        pytest.param(True, id="boolean"),
        pytest.param(2147483648, id="above_int32"),
        pytest.param(None, id="null"),
    ],
)
def test_club_id_is_rejected(club_id) -> None:
    with pytest.raises(ValidationError):
        BuyPlayerRequest.model_validate({**VALID, "club_id": club_id})


def test_club_id_sent_as_a_whole_decimal_is_accepted() -> None:
    assert BuyPlayerRequest.model_validate({**VALID, "club_id": 3.0}).club_id == 3


@pytest.mark.parametrize("field", ["club_id", "loyalty_until"])
def test_missing_field_is_rejected(field) -> None:
    body = {key: value for key, value in VALID.items() if key != field}

    with pytest.raises(ValidationError):
        BuyPlayerRequest.model_validate(body)


def test_other_fields_are_ignored() -> None:
    request = BuyPlayerRequest.model_validate({**VALID, "value": 1, "fee": 1, "player_id": 9})

    assert not hasattr(request, "value")
    assert not hasattr(request, "player_id")
