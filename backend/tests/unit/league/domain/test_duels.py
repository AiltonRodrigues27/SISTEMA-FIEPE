import pytest

from app.modules.league.domain.duels import Team, count_goals, play_duels
from app.modules.players.domain.enums import PhysicalCondition, Position

GOL, ZAG, LAT, MEI, ATA = (
    Position.GOL,
    Position.ZAG,
    Position.LAT,
    Position.MEI,
    Position.ATA,
)


def summarize_duels(duels):
    return [
        (
            duel.order,
            duel.attacking_club_id,
            duel.attacker.player_name,
            duel.attacker.attribute,
            duel.attacker.value,
            duel.defender.player_name,
            duel.defender.attribute,
            duel.defender.value,
            duel.goal,
        )
        for duel in duels
    ]


def test_duels_follow_the_example_of_the_statement(eagles, delta) -> None:
    duels = play_duels(eagles, delta)

    assert summarize_duels(duels) == [
        (1, 1, "Otto Rangel", "shooting", 75, "Ivo Teles", "defending", 72, True),
        (2, 1, "Lauro Neves", "passing", 82, "Hugo Vaz", "defending", 84, False),
        (3, 1, "Davi Lins", "dribbling", 63, "Lino Matos", "defending", 63, False),
        (4, 2, "Ugo Falcão", "shooting", 81, "Rui Prado", "defending", 77, True),
        (5, 2, "Nei Soares", "passing", 70, "Téo Brandão", "defending", 84, False),
        (6, 2, "Lino Matos", "dribbling", 79, "Davi Lins", "defending", 56, True),
    ]


def test_goals_of_each_club_are_counted_from_the_duels_it_attacked(eagles, delta) -> None:
    duels = play_duels(eagles, delta)

    assert count_goals(duels, eagles.club_id) == 1
    assert count_goals(duels, delta.club_id) == 2


def test_the_same_teams_always_give_the_same_duels(eagles, delta) -> None:
    assert play_duels(eagles, delta) == play_duels(eagles, delta)


def test_the_goals_do_not_depend_on_who_is_the_home_team(eagles, delta) -> None:
    swapped = play_duels(delta, eagles)

    assert count_goals(swapped, eagles.club_id) == 1
    assert count_goals(swapped, delta.club_id) == 2
    assert [duel.attacking_club_id for duel in swapped] == [2, 2, 2, 1, 1, 1]


def test_the_orders_run_from_one_to_six_with_three_attacks_per_club(eagles, delta) -> None:
    duels = play_duels(eagles, delta)

    assert [duel.order for duel in duels] == [1, 2, 3, 4, 5, 6]
    assert [duel.attacking_club_id for duel in duels] == [1, 1, 1, 2, 2, 2]


@pytest.mark.parametrize(
    ("condition", "value", "expected"),
    [
        pytest.param(PhysicalCondition.APTO, 74, 74, id="apto_keeps_the_value"),
        pytest.param(PhysicalCondition.MAL_CONDICIONADO, 74, 63, id="74_to_63"),
        pytest.param(PhysicalCondition.MAL_CONDICIONADO, 66, 56, id="66_to_56"),
        pytest.param(PhysicalCondition.MAL_CONDICIONADO, 50, 43, id="42.5_rounds_up_to_43"),
        pytest.param(PhysicalCondition.MAL_CONDICIONADO, 10, 9, id="8.5_rounds_up_to_9"),
        pytest.param(PhysicalCondition.MAL_CONDICIONADO, 1, 1, id="0.85_rounds_up_to_1"),
        pytest.param(PhysicalCondition.MAL_CONDICIONADO, 99, 84, id="84.15_rounds_to_84"),
    ],
)
def test_a_mal_condicionado_starter_plays_with_fifteen_percent_less(
    make_starter, condition, value, expected
) -> None:
    starter = make_starter(1, "Ana Lima", ATA, condition, shooting=value)

    assert starter.value_of("shooting") == expected


def test_the_condition_effect_does_not_change_the_starter(make_starter) -> None:
    starter = make_starter(1, "Ana Lima", ATA, PhysicalCondition.MAL_CONDICIONADO, shooting=74)

    starter.value_of("shooting")

    assert starter.shooting == 74


@pytest.mark.parametrize(
    ("attack", "defense", "goal"),
    [
        pytest.param(81, 80, True, id="attack_above_defense"),
        pytest.param(80, 80, False, id="tied_duel_is_not_a_goal"),
        pytest.param(79, 80, False, id="attack_below_defense"),
    ],
)
def test_a_duel_is_a_goal_only_when_the_attack_is_greater(
    make_starter, attack, defense, goal
) -> None:
    home = Team.from_starters(
        1,
        "2-1-1",
        [
            make_starter(1, "Ana Lima", GOL),
            make_starter(2, "Beto Souza", ZAG),
            make_starter(3, "Caio Dias", LAT),
            make_starter(4, "Davi Reis", MEI),
            make_starter(5, "Edu Luz", ATA, shooting=attack),
        ],
    )
    away = Team.from_starters(
        2,
        "2-1-1",
        [
            make_starter(6, "Fabio Cruz", GOL, defending=defense),
            make_starter(7, "Gil Mota", ZAG),
            make_starter(8, "Hugo Neri", LAT),
            make_starter(9, "Ivo Pena", MEI),
            make_starter(10, "Jonas Roque", ATA),
        ],
    )

    first_duel = play_duels(home, away)[0]

    assert (first_duel.attacker.value, first_duel.defender.value) == (attack, defense)
    assert first_duel.goal is goal


@pytest.mark.parametrize(
    ("formation", "field_positions", "attack_attributes", "second_defender"),
    [
        pytest.param("3-1", (ZAG, LAT, LAT, ATA), ("shooting", "dribbling", "dribbling"), LAT),
        pytest.param("2-2", (ZAG, LAT, ATA, ATA), ("shooting", "shooting", "dribbling"), LAT),
        pytest.param("2-1-1", (ZAG, LAT, MEI, ATA), ("shooting", "passing", "dribbling"), LAT),
        pytest.param("1-2-1", (ZAG, MEI, MEI, ATA), ("shooting", "passing", "passing"), MEI),
    ],
)
def test_attackers_and_defenders_follow_the_table_of_each_formation(
    make_starter, delta, formation, field_positions, attack_attributes, second_defender
) -> None:
    team = Team.from_starters(
        1,
        formation,
        [make_starter(1, "Ana Lima", GOL)]
        + [
            make_starter(10 + index, f"Jogador {name}", position)
            for index, (name, position) in enumerate(zip("ABCD", field_positions, strict=True))
        ],
    )

    duels = play_duels(team, delta)
    away_duels = play_duels(delta, team)

    assert [duel.attacker.attribute for duel in duels[:3]] == list(attack_attributes)
    assert [duel.attacker.position for duel in duels[:3]] == [
        field_positions[3],
        field_positions[2],
        field_positions[1],
    ]
    assert [duel.defender.position for duel in away_duels[:3]] == [GOL, ZAG, second_defender]


def test_the_defender_always_uses_the_defense_attribute(eagles, delta) -> None:
    duels = play_duels(eagles, delta)

    assert {duel.defender.attribute for duel in duels} == {"defending"}


def test_the_duels_carry_the_name_position_and_condition_of_the_moment(eagles, delta) -> None:
    davi_as_attacker = play_duels(eagles, delta)[2].attacker

    assert (davi_as_attacker.player_id, davi_as_attacker.position, davi_as_attacker.condition) == (
        31,
        LAT,
        PhysicalCondition.MAL_CONDICIONADO,
    )
