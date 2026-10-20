from decimal import Decimal

import pytest

from app.modules.players.adapters.inbound.http.list_query import parse_list_players_query
from app.modules.players.application.list_players import ListPlayersQuery
from app.modules.players.domain.enums import PhysicalCondition, Position
from app.modules.players.domain.errors import InvalidListQuery
from app.modules.players.domain.listing import PlayerFilters, SortKey

INVALID_PARAMETERS = [
    ("search", ""),
    ("search", " "),
    ("search", "a"),
    ("search", "a" * 101),
    ("search", "Meia\tLua"),
    ("position", ""),
    ("position", "mei"),
    ("position", "XXX"),
    ("condition", ""),
    ("condition", "doente"),
    ("free", ""),
    ("free", "TRUE"),
    ("free", "1"),
    ("free", "yes"),
    ("club_id", ""),
    ("club_id", "0"),
    ("club_id", "01"),
    ("club_id", "-1"),
    ("club_id", "+1"),
    ("club_id", "1.5"),
    ("club_id", "1e3"),
    ("club_id", "abc"),
    ("club_id", "2147483648"),
    ("min_age", "15"),
    ("min_age", "46"),
    ("min_age", "016"),
    ("min_age", " 20"),
    ("max_age", "15"),
    ("max_age", "46"),
    ("max_age", "30.0"),
    ("min_value", "-1"),
    ("min_value", "1,5"),
    ("min_value", "1e2"),
    ("min_value", "00.5"),
    ("min_value", "551"),
    ("min_value", "10.555"),
    ("min_value", ".5"),
    ("min_value", "+5"),
    ("max_value", ""),
    ("max_value", "551"),
    ("sort", ""),
    ("sort", "POSITION"),
    ("sort", "name,"),
    ("sort", "name, age_asc"),
    ("sort", "value_asc,value_desc"),
    ("sort", "name,name"),
    ("sort", "name,age_asc,position"),
    ("sort", "price"),
    ("page", ""),
    ("page", "0"),
    ("page", "-1"),
    ("page", "01"),
    ("page", "1.5"),
    ("page", "abc"),
    ("limit", ""),
    ("limit", "0"),
    ("limit", "51"),
    ("limit", "010"),
    ("limit", "abc"),
]


def test_defaults_when_there_are_no_parameters() -> None:
    query = parse_list_players_query({})

    assert query == ListPlayersQuery(
        filters=PlayerFilters(), sort=(SortKey.NAME,), page=1, limit=10
    )


def test_every_parameter_is_read() -> None:
    params = {
        "search": "  lua  ",
        "position": "MEI",
        "condition": "MAL_CONDICIONADO",
        "free": "false",
        "club_id": "3",
        "min_age": "20",
        "max_age": "30",
        "min_value": "10.5",
        "max_value": "100",
        "sort": "position,value_desc",
        "page": "2",
        "limit": "5",
    }

    query = parse_list_players_query(params)

    assert query == ListPlayersQuery(
        filters=PlayerFilters(
            search="lua",
            position=Position.MEI,
            condition=PhysicalCondition.MAL_CONDICIONADO,
            free=False,
            club_id=3,
            min_age=20,
            max_age=30,
            min_value=Decimal("10.5"),
            max_value=Decimal("100"),
        ),
        sort=(SortKey.POSITION, SortKey.VALUE_DESC),
        page=2,
        limit=5,
    )


def test_search_text_is_cleaned() -> None:
    query = parse_list_players_query({"search": "  joao   silva "})

    assert query.filters.search == "joao silva"


def test_only_one_bound_leaves_the_other_open() -> None:
    query = parse_list_players_query({"min_age": "20", "max_value": "50"})

    assert query.filters.min_age == 20
    assert query.filters.max_age is None
    assert query.filters.min_value is None
    assert query.filters.max_value == Decimal("50")


def test_unknown_parameters_are_ignored() -> None:
    query = parse_list_players_query({"foo": "bar", "Page": "2", "POSITION": "xx"})

    assert query == parse_list_players_query({})


@pytest.mark.parametrize(
    ("name", "value"),
    [pytest.param(name, value, id=f"{name}={value!r}") for name, value in INVALID_PARAMETERS],
)
def test_invalid_parameter_is_rejected(name, value) -> None:
    with pytest.raises(InvalidListQuery):
        parse_list_players_query({name: value})


@pytest.mark.parametrize(
    ("name", "value", "check"),
    [
        pytest.param("limit", "1", lambda query: query.limit == 1, id="smallest_limit"),
        pytest.param("limit", "50", lambda query: query.limit == 50, id="largest_limit"),
        pytest.param("page", "1", lambda query: query.page == 1, id="first_page"),
        pytest.param("page", "999999", lambda query: query.page == 999999, id="far_page"),
        pytest.param("min_age", "16", lambda query: query.filters.min_age == 16, id="min_age"),
        pytest.param("max_age", "45", lambda query: query.filters.max_age == 45, id="max_age"),
        pytest.param(
            "min_value", "0", lambda query: query.filters.min_value == Decimal(0), id="zero"
        ),
        pytest.param(
            "min_value", "0.5", lambda query: query.filters.min_value == Decimal("0.5"), id="half"
        ),
        pytest.param(
            "max_value",
            "10.55",
            lambda query: query.filters.max_value == Decimal("10.55"),
            id="two_decimals",
        ),
        pytest.param(
            "max_value", "550", lambda query: query.filters.max_value == Decimal(550), id="top"
        ),
        pytest.param("free", "true", lambda query: query.filters.free is True, id="free_true"),
        pytest.param("sort", "age_asc", lambda query: query.sort == (SortKey.AGE_ASC,), id="age"),
    ],
)
def test_valid_edge_values_are_accepted(name, value, check) -> None:
    assert check(parse_list_players_query({name: value}))


@pytest.mark.parametrize(
    "params",
    [
        pytest.param({"min_age": "30", "max_age": "20"}, id="min_age_above_max_age"),
        pytest.param({"min_value": "60", "max_value": "50"}, id="min_value_above_max_value"),
        pytest.param({"free": "true", "club_id": "1"}, id="free_true_with_club"),
    ],
)
def test_contradictory_combination_is_rejected(params) -> None:
    with pytest.raises(InvalidListQuery):
        parse_list_players_query(params)


@pytest.mark.parametrize(
    "params",
    [
        pytest.param({"min_age": "30", "max_age": "30"}, id="equal_ages"),
        pytest.param({"min_value": "5", "max_value": "5"}, id="equal_values"),
        pytest.param({"free": "false", "club_id": "1"}, id="free_false_with_club"),
    ],
)
def test_compatible_combination_is_accepted(params) -> None:
    parse_list_players_query(params)
