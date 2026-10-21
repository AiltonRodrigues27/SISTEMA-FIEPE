import pytest
from pydantic import ValidationError

from app.modules.league.adapters.inbound.http.schemas import PlayMatchRequest


def parse(**fields):
    return PlayMatchRequest.model_validate({"home_club_id": 1, "away_club_id": 2, **fields})


def test_valid_body_is_parsed() -> None:
    request = parse()

    assert (request.home_club_id, request.away_club_id) == (1, 2)


def test_ids_sent_as_whole_decimals_are_accepted() -> None:
    request = parse(home_club_id=3.0)

    assert request.home_club_id == 3


def test_two_equal_ids_pass_the_schema_because_the_rule_belongs_to_the_use_case() -> None:
    request = parse(away_club_id=1)

    assert request.home_club_id == request.away_club_id == 1


@pytest.mark.parametrize("field", ["home_club_id", "away_club_id"])
@pytest.mark.parametrize(
    "value",
    [
        pytest.param(0, id="zero"),
        pytest.param(-1, id="negative"),
        pytest.param("1", id="text"),
        pytest.param(1.5, id="fraction"),
        pytest.param(True, id="boolean"),
        pytest.param(None, id="null"),
        pytest.param(2147483648, id="above_int32"),
        pytest.param([1], id="list"),
    ],
)
def test_invalid_id_is_rejected(field, value) -> None:
    with pytest.raises(ValidationError):
        parse(**{field: value})


@pytest.mark.parametrize("missing", ["home_club_id", "away_club_id"])
def test_missing_field_is_rejected(missing) -> None:
    body = {"home_club_id": 1, "away_club_id": 2}
    del body[missing]

    with pytest.raises(ValidationError):
        PlayMatchRequest.model_validate(body)


def test_other_fields_are_ignored() -> None:
    request = parse(home_goals=9, result="MANDANTE")

    assert not hasattr(request, "home_goals")
