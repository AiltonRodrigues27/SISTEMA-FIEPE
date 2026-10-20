import pytest

from app.modules.clubs.adapters.inbound.http.list_query import parse_club_sort
from app.modules.clubs.domain.errors import InvalidClubQuery
from app.modules.clubs.domain.listing import ClubSortKey


def test_sort_defaults_to_name() -> None:
    assert parse_club_sort({}) is ClubSortKey.NAME


@pytest.mark.parametrize("sort", list(ClubSortKey))
def test_every_sort_value_is_accepted(sort) -> None:
    assert parse_club_sort({"sort": sort.value}) is sort


@pytest.mark.parametrize("value", ["", "NAME", "Name", "price", "net_worth", "name,net_worth_asc"])
def test_invalid_sort_is_rejected(value) -> None:
    with pytest.raises(InvalidClubQuery):
        parse_club_sort({"sort": value})


def test_unknown_parameters_are_ignored() -> None:
    assert parse_club_sort({"foo": "bar", "Sort": "xx"}) is ClubSortKey.NAME
