from decimal import Decimal

import pytest

from app.modules.market.domain.calculations import (
    calculate_commission,
    calculate_purchase_fee,
    calculate_sale_outcome,
    ensure_within_cash_limit,
)
from app.modules.market.domain.errors import CashLimitExceeded


@pytest.mark.parametrize(
    ("market_value", "fee"),
    [
        pytest.param("28.00", "0.00", id="below_the_threshold"),
        pytest.param("30.00", "0.00", id="exactly_the_threshold_has_no_fee"),
        pytest.param("30.01", "1.50", id="just_above_the_threshold"),
        pytest.param("37.00", "1.85", id="example_of_the_statement"),
        pytest.param("47.62", "2.38", id="rounds_down"),
        pytest.param("48.00", "2.40", id="exact_five_percent"),
    ],
)
def test_purchase_fee_is_five_percent_only_above_thirty(market_value, fee) -> None:
    assert calculate_purchase_fee(Decimal(market_value)) == Decimal(fee)


@pytest.mark.parametrize(
    ("cash", "total_cost"),
    [
        pytest.param("300.00", "28.00", id="far_below_the_limit"),
        pytest.param("300.00", "38.85", id="example_of_the_statement"),
        pytest.param("100.00", "50.00", id="exactly_half_of_the_cash"),
        pytest.param("261.15", "130.57", id="just_below_half"),
    ],
)
def test_cash_limit_accepts_up_to_half_of_the_cash(cash, total_cost) -> None:
    ensure_within_cash_limit(Decimal(total_cost), Decimal(cash))


@pytest.mark.parametrize(
    ("cash", "total_cost"),
    [
        pytest.param("100.00", "50.40", id="table_of_the_statement"),
        pytest.param("261.15", "130.58", id="limit_is_not_rounded"),
    ],
)
def test_cash_limit_rejects_more_than_half_of_the_cash(cash, total_cost) -> None:
    with pytest.raises(CashLimitExceeded):
        ensure_within_cash_limit(Decimal(total_cost), Decimal(cash))


@pytest.mark.parametrize(
    ("profit", "commission"),
    [
        pytest.param("3.00", "0.30", id="ten_percent"),
        pytest.param("3.85", "0.39", id="rounds_half_up"),
        pytest.param("10.00", "1.00", id="end_of_the_first_band"),
        pytest.param("10.01", "1.00", id="a_cent_in_the_second_band"),
        pytest.param("15.00", "2.00", id="both_bands"),
        pytest.param("-7.50", "0.00", id="no_commission_on_a_loss"),
        pytest.param("0.00", "0.00", id="no_commission_without_profit"),
    ],
)
def test_commission_is_progressive_and_only_on_profit(profit, commission) -> None:
    assert calculate_commission(Decimal(profit)) == Decimal(commission)


@pytest.mark.parametrize(
    ("purchase", "value", "penalty", "profit", "commission", "credit"),
    [
        pytest.param("37.00", "40.00", "4.00", "3.00", "0.30", "35.70", id="statement_example"),
        pytest.param("50.00", "42.50", "8.50", "-7.50", "0.00", "34.00", id="sale_at_a_loss"),
        pytest.param("26.15", "30.00", "1.50", "3.85", "0.39", "28.11", id="commission_rounded"),
        pytest.param("25.00", "25.00", "0.00", "0.00", "0.00", "25.00", id="no_penalty"),
        pytest.param("60.00", "75.00", "10.00", "15.00", "2.00", "63.00", id="capped_penalty"),
    ],
)
def test_sale_outcome_follows_the_table_of_the_statement(
    purchase, value, penalty, profit, commission, credit
) -> None:
    outcome = calculate_sale_outcome(Decimal(value), Decimal(purchase), Decimal(penalty))

    assert outcome.profit == Decimal(profit)
    assert outcome.commission == Decimal(commission)
    assert outcome.credit == Decimal(credit)
    assert outcome.penalty == Decimal(penalty)
