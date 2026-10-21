import pytest

from app.modules.league.adapters.inbound.http.list_query import parse_match_club_id
from app.modules.league.domain.errors import InvalidMatchQuery

INVALID_VALUES = ["", "0", "01", "-1", "+1", "1.5", "1e2", "abc", " 1", "1 ", "2147483648"]


def test_without_the_parameter_there_is_no_filter() -> None:
    assert parse_match_club_id({}) is None


def test_unknown_parameters_are_ignored() -> None:
    assert parse_match_club_id({"foo": "1", "Club_id": "x"}) is None


@pytest.mark.parametrize(("value", "expected"), [("1", 1), ("25", 25), ("2147483647", 2147483647)])
def test_a_positive_integer_written_with_digits_is_accepted(value, expected) -> None:
    assert parse_match_club_id({"club_id": value}) == expected


@pytest.mark.parametrize("value", INVALID_VALUES)
def test_club_id_outside_the_rules_is_rejected(value) -> None:
    with pytest.raises(InvalidMatchQuery):
        parse_match_club_id({"club_id": value})
