from decimal import Decimal

import pytest

from app.modules.players.domain.calculations import (
    OVERALL_WEIGHTS,
    calculate_base_value,
    calculate_market_value,
    calculate_overall,
)
from app.modules.players.domain.entities import Attributes
from app.modules.players.domain.enums import PhysicalCondition, Position

APTO = PhysicalCondition.APTO
MAL = PhysicalCondition.MAL_CONDICIONADO
DOENTE = PhysicalCondition.DOENTE


@pytest.mark.parametrize(
    ("base_value", "condition", "agility", "age", "expected"),
    [
        ("82.00", APTO, 20, 25, "82.00"),
        ("82.00", APTO, 50, 19, "90.20"),
        ("82.00", MAL, 50, 25, "69.70"),
        ("82.00", MAL, 80, 21, "84.05"),
        ("82.00", MAL, 30, 33, "53.30"),
        ("82.00", DOENTE, 90, 25, "69.70"),
        ("82.00", DOENTE, 30, 25, "49.20"),
        ("82.00", DOENTE, 10, 40, "49.20"),
        ("9.50", MAL, 85, 25, "8.79"),
        ("1.00", MAL, 50, 35, "1.00"),
    ],
)
def test_calculate_market_value_matches_documented_examples(
    base_value: str, condition: PhysicalCondition, agility: int, age: int, expected: str
) -> None:
    result = calculate_market_value(Decimal(base_value), condition, agility, age)

    assert result == Decimal(expected)


@pytest.mark.parametrize(
    ("condition", "agility", "age", "expected"),
    [
        (MAL, 79, 25, "85.00"),
        (MAL, 80, 25, "92.50"),
        (MAL, 31, 25, "85.00"),
        (MAL, 30, 25, "75.00"),
        (APTO, 50, 21, "110.00"),
        (APTO, 50, 22, "100.00"),
        (APTO, 50, 31, "100.00"),
        (APTO, 50, 32, "90.00"),
    ],
)
def test_calculate_market_value_respects_agility_and_age_boundaries(
    condition: PhysicalCondition, agility: int, age: int, expected: str
) -> None:
    result = calculate_market_value(Decimal("100.00"), condition, agility, age)

    assert result == Decimal(expected)


@pytest.mark.parametrize(
    ("position", "attributes", "expected"),
    [
        (Position.MEI, Attributes(68, 65, 80, 78, 52, 60), 73),
        (Position.ATA, Attributes(78, 75, 73, 82, 48, 68), 76),
        (Position.LAT, Attributes(72, 70, 78, 76, 70, 66), 72),
        (Position.ZAG, Attributes(50, 90, 60, 40, 80, 75), 73),
        (Position.GOL, Attributes(55, 30, 65, 40, 72, 68), 68),
    ],
)
def test_calculate_overall_matches_documented_examples(
    position: Position, attributes: Attributes, expected: int
) -> None:
    assert calculate_overall(position, attributes) == expected


@pytest.mark.parametrize("position", list(Position))
def test_overall_weights_sum_to_100(position: Position) -> None:
    assert sum(OVERALL_WEIGHTS[position]) == 100


@pytest.mark.parametrize(
    ("overall", "potential", "age", "expected"),
    [
        (75, 86, 25, "40.00"),
        (60, 70, 30, "10.00"),
        (61, 70, 30, "12.00"),
        (76, 80, 22, "46.00"),
        (85, 92, 27, "100.00"),
        (70, 84, 21, "34.20"),
        (70, 84, 22, "30.00"),
        (45, 90, 18, "3.63"),
        (40, 66, 36, "1.00"),
    ],
)
def test_calculate_base_value_matches_documented_examples(
    overall: int, potential: int, age: int, expected: str
) -> None:
    assert calculate_base_value(overall, potential, age) == Decimal(expected)
