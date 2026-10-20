from decimal import Decimal

import pytest

from app.modules.players.domain.entities import Attributes, Player
from app.modules.players.domain.enums import PhysicalCondition, Position
from app.modules.players.domain.listing import PlayerFilters, SortKey, matches, sort_players


def build_player(
    player_id: int = 1,
    name: str = "Ana Lima",
    position: Position = Position.MEI,
    age: int = 25,
    condition: PhysicalCondition = PhysicalCondition.APTO,
    agility: int = 50,
    base_value: str = "40.00",
    club_id: int | None = None,
) -> Player:
    return Player(
        id=player_id,
        name=name,
        position=position,
        agility=agility,
        age=age,
        condition=condition,
        club_id=club_id,
        base_value=Decimal(base_value),
        attributes=Attributes(70, 68, 82, 79, 55, 64),
        potential=86,
    )


def names(players: list[Player]) -> list[str]:
    return [player.name for player in players]


def test_empty_filters_match_every_player() -> None:
    assert matches(build_player(), PlayerFilters())


@pytest.mark.parametrize(
    ("search", "name", "expected"),
    [
        pytest.param("joao", "João Silva", True, id="ignores_accents"),
        pytest.param("JOÃO", "joao silva", True, id="ignores_accents_and_case_on_both_sides"),
        pytest.param("LUA", "Meia Lua", True, id="ignores_case"),
        pytest.param("ilv", "João Silva", True, id="inside_the_name"),
        pytest.param("ze", "Zé Foguete", True, id="accent_in_the_name"),
        pytest.param("silva joao", "João Silva", False, id="order_matters"),
        pytest.param("xyz", "João Silva", False, id="not_found"),
    ],
)
def test_search_looks_inside_the_name_ignoring_case_and_accents(search, name, expected) -> None:
    assert matches(build_player(name=name), PlayerFilters(search=search)) is expected


@pytest.mark.parametrize(
    ("filters", "player", "expected"),
    [
        pytest.param(
            PlayerFilters(position=Position.ATA),
            build_player(position=Position.ATA),
            True,
            id="position_equal",
        ),
        pytest.param(
            PlayerFilters(position=Position.ATA),
            build_player(position=Position.MEI),
            False,
            id="position_different",
        ),
        pytest.param(
            PlayerFilters(condition=PhysicalCondition.DOENTE),
            build_player(condition=PhysicalCondition.DOENTE),
            True,
            id="condition_equal",
        ),
        pytest.param(
            PlayerFilters(condition=PhysicalCondition.DOENTE),
            build_player(condition=PhysicalCondition.APTO),
            False,
            id="condition_different",
        ),
        pytest.param(PlayerFilters(free=True), build_player(club_id=None), True, id="free_true"),
        pytest.param(PlayerFilters(free=True), build_player(club_id=3), False, id="free_true_club"),
        pytest.param(PlayerFilters(free=False), build_player(club_id=3), True, id="free_false"),
        pytest.param(
            PlayerFilters(free=False), build_player(club_id=None), False, id="free_false_no_club"
        ),
        pytest.param(PlayerFilters(club_id=3), build_player(club_id=3), True, id="club_equal"),
        pytest.param(PlayerFilters(club_id=3), build_player(club_id=4), False, id="club_other"),
        pytest.param(PlayerFilters(club_id=3), build_player(club_id=None), False, id="club_none"),
        pytest.param(PlayerFilters(min_age=20), build_player(age=20), True, id="min_age_edge"),
        pytest.param(PlayerFilters(min_age=20), build_player(age=19), False, id="below_min_age"),
        pytest.param(PlayerFilters(max_age=30), build_player(age=30), True, id="max_age_edge"),
        pytest.param(PlayerFilters(max_age=30), build_player(age=31), False, id="above_max_age"),
    ],
)
def test_each_filter_keeps_or_drops_the_player(filters, player, expected) -> None:
    assert matches(player, filters) is expected


MARKET_VALUE_69_70 = build_player(
    condition=PhysicalCondition.MAL_CONDICIONADO, agility=50, age=25, base_value="82.00"
)


@pytest.mark.parametrize(
    ("filters", "expected"),
    [
        pytest.param(PlayerFilters(min_value=Decimal("69.70")), True, id="min_value_edge"),
        pytest.param(PlayerFilters(min_value=Decimal("69.71")), False, id="below_min_value"),
        pytest.param(PlayerFilters(max_value=Decimal("69.70")), True, id="max_value_edge"),
        pytest.param(PlayerFilters(max_value=Decimal("69.69")), False, id="above_max_value"),
        pytest.param(PlayerFilters(max_value=Decimal("70")), True, id="uses_market_not_base_value"),
    ],
)
def test_value_filters_use_the_market_value(filters, expected) -> None:
    assert matches(MARKET_VALUE_69_70, filters) is expected


def test_filters_must_all_hold_at_the_same_time() -> None:
    player = build_player(position=Position.ATA, age=25)

    assert matches(player, PlayerFilters(position=Position.ATA, min_age=20, max_age=30))
    assert not matches(player, PlayerFilters(position=Position.ATA, min_age=30))
    assert not matches(player, PlayerFilters(position=Position.MEI, min_age=20))


def test_sort_by_name_ignores_case_and_accents_and_follows_unicode_order() -> None:
    players = [
        build_player(1, "Gama Souza"),
        build_player(2, "Épsilon Lima"),
        build_player(3, "delta Costa"),
        build_player(4, "Ana-Maria Reis"),
        build_player(5, "Ana Lima"),
    ]

    result = sort_players(players, (SortKey.NAME,))

    assert names(result) == [
        "Ana Lima",
        "Ana-Maria Reis",
        "delta Costa",
        "Épsilon Lima",
        "Gama Souza",
    ]


def test_sort_without_criteria_orders_by_name() -> None:
    players = [build_player(1, "Beto Souza"), build_player(2, "Ana Lima")]

    assert names(sort_players(players, ())) == ["Ana Lima", "Beto Souza"]


def test_sort_breaks_equal_names_by_id() -> None:
    players = [build_player(2, "Águias Fc"), build_player(1, "Aguias Fc")]

    result = sort_players(players, (SortKey.NAME,))

    assert [player.id for player in result] == [1, 2]


def test_sort_by_position_follows_goalkeeper_to_forward_order() -> None:
    players = [
        build_player(1, "Ata Lima", position=Position.ATA),
        build_player(2, "Mei Lima", position=Position.MEI),
        build_player(3, "Gol Lima", position=Position.GOL),
        build_player(4, "Lat Lima", position=Position.LAT),
        build_player(5, "Zag Lima", position=Position.ZAG),
    ]

    result = sort_players(players, (SortKey.POSITION,))

    assert [player.position for player in result] == [
        Position.GOL,
        Position.ZAG,
        Position.LAT,
        Position.MEI,
        Position.ATA,
    ]


def test_sort_by_position_breaks_ties_by_name_then_id() -> None:
    players = [
        build_player(3, "Beto Souza", position=Position.MEI),
        build_player(2, "Ana Lima", position=Position.MEI),
        build_player(1, "Ana Lima", position=Position.MEI),
    ]

    result = sort_players(players, (SortKey.POSITION,))

    assert [player.id for player in result] == [1, 2, 3]


def test_sort_by_market_value_ascending_and_descending() -> None:
    players = [
        build_player(1, "Ana Lima", base_value="20.00"),
        build_player(2, "Beto Souza", base_value="30.00"),
        build_player(3, "Caio Dias", base_value="10.00"),
    ]

    ascending = sort_players(players, (SortKey.VALUE_ASC,))
    descending = sort_players(players, (SortKey.VALUE_DESC,))

    assert names(ascending) == ["Caio Dias", "Ana Lima", "Beto Souza"]
    assert names(descending) == ["Beto Souza", "Ana Lima", "Caio Dias"]


def test_sort_by_value_uses_the_market_value_not_the_base_value() -> None:
    healthy = build_player(1, "Ana Lima", base_value="40.00")
    sick = build_player(
        2, "Beto Souza", condition=PhysicalCondition.DOENTE, agility=50, base_value="50.00"
    )

    result = sort_players([sick, healthy], (SortKey.VALUE_DESC,))

    assert names(result) == ["Ana Lima", "Beto Souza"]


def test_sort_descending_breaks_ties_by_name_ascending() -> None:
    players = [
        build_player(1, "Beto Souza", base_value="30.00"),
        build_player(2, "Ana Lima", base_value="30.00"),
    ]

    result = sort_players(players, (SortKey.VALUE_DESC,))

    assert names(result) == ["Ana Lima", "Beto Souza"]


def test_sort_by_age_ascending_and_descending() -> None:
    players = [
        build_player(1, "Ana Lima", age=30),
        build_player(2, "Beto Souza", age=20),
        build_player(3, "Caio Dias", age=25),
    ]

    ascending = sort_players(players, (SortKey.AGE_ASC,))
    descending = sort_players(players, (SortKey.AGE_DESC,))

    assert names(ascending) == ["Beto Souza", "Caio Dias", "Ana Lima"]
    assert names(descending) == ["Ana Lima", "Caio Dias", "Beto Souza"]


def test_second_criterion_only_breaks_ties_of_the_first() -> None:
    players = [
        build_player(1, "Ana Lima", position=Position.MEI, base_value="40.00"),
        build_player(2, "Beto Souza", position=Position.MEI, base_value="20.00"),
        build_player(3, "Caio Dias", position=Position.GOL, base_value="10.00"),
    ]

    result = sort_players(players, (SortKey.POSITION, SortKey.VALUE_DESC))

    assert names(result) == ["Caio Dias", "Ana Lima", "Beto Souza"]


def test_sort_does_not_change_the_given_list() -> None:
    players = [build_player(1, "Beto Souza"), build_player(2, "Ana Lima")]

    sort_players(players, (SortKey.NAME,))

    assert names(players) == ["Beto Souza", "Ana Lima"]
