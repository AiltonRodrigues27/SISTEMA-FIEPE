from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from app.modules.clubs.domain.contract import calculate_penalty, penalty_percent, remaining_days
from app.shared.domain.brasilia_time import BRASILIA

NOW = datetime(2026, 11, 5, 16, 40, tzinfo=BRASILIA)


@pytest.mark.parametrize(
    ("remaining", "days", "percent"),
    [
        pytest.param(timedelta(days=-3), 0, 0, id="already_passed"),
        pytest.param(timedelta(0), 0, 0, id="exactly_now"),
        pytest.param(timedelta(minutes=1), 1, 5, id="one_minute_left_counts_a_day"),
        pytest.param(timedelta(days=10, hours=2), 11, 5, id="ten_days_and_two_hours"),
        pytest.param(timedelta(days=30), 30, 5, id="exactly_thirty_days"),
        pytest.param(timedelta(days=30, minutes=1), 31, 10, id="thirty_days_and_a_minute"),
        pytest.param(timedelta(days=180), 180, 10, id="exactly_one_hundred_eighty_days"),
        pytest.param(timedelta(days=180, minutes=1), 181, 20, id="one_hundred_eighty_and_a_minute"),
        pytest.param(timedelta(days=200), 200, 20, id="two_hundred_days"),
        pytest.param(timedelta(days=116, hours=17, minutes=35), 117, 10, id="rounds_up"),
    ],
)
def test_remaining_days_round_up_and_set_the_penalty_percent(remaining, days, percent) -> None:
    loyalty_until = NOW + remaining

    assert remaining_days(loyalty_until, NOW) == days
    assert penalty_percent(days) == percent


@pytest.mark.parametrize(
    ("market_value", "days", "penalty"),
    [
        pytest.param("40.00", 100, "4.00", id="ten_percent"),
        pytest.param("42.50", 200, "8.50", id="twenty_percent"),
        pytest.param("30.00", 10, "1.50", id="five_percent"),
        pytest.param("25.00", 0, "0.00", id="no_penalty_when_the_loyalty_is_over"),
        pytest.param("75.00", 200, "10.00", id="capped_at_ten"),
        pytest.param("8.7875", 10, "0.44", id="rounds_half_up"),
    ],
)
def test_penalty_is_rounded_and_capped_at_ten(market_value, days, penalty) -> None:
    assert calculate_penalty(Decimal(market_value), days) == Decimal(penalty)
