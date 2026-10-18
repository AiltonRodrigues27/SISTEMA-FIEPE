from decimal import Decimal

import pytest

from app.shared.domain.rounding import round_half_up


@pytest.mark.parametrize(
    ("value", "decimal_places", "expected"),
    [
        ("14.775", 2, "14.78"),
        ("0.385", 2, "0.39"),
        ("3.625", 2, "3.63"),
        ("72.5", 0, "73"),
        ("72.49", 0, "72"),
        ("-0.385", 2, "-0.39"),
    ],
)
def test_round_half_up_rounds_ties_away_from_zero(
    value: str, decimal_places: int, expected: str
) -> None:
    assert round_half_up(Decimal(value), decimal_places) == Decimal(expected)
