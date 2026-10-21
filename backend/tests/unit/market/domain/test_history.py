from datetime import datetime
from decimal import Decimal

from app.modules.market.domain.calculations import calculate_sale_outcome
from app.modules.market.domain.history import summarize
from app.modules.market.domain.transaction import Transaction
from app.shared.domain.brasilia_time import BRASILIA

MOMENT = datetime(2026, 11, 2, 10, 15, tzinfo=BRASILIA)


def purchase(value: str = "37.00", fee: str = "1.85") -> Transaction:
    return Transaction.purchase(
        club_id=1,
        player_id=2,
        player_name="Meia Lua",
        value=Decimal(value),
        fee=Decimal(fee),
        created_at=MOMENT,
    )


def sale(value: str = "40.00", purchase_value: str = "37.00", penalty: str = "4.00") -> Transaction:
    outcome = calculate_sale_outcome(Decimal(value), Decimal(purchase_value), Decimal(penalty))
    return Transaction.sale(
        club_id=1, player_id=2, player_name="Meia Lua", outcome=outcome, created_at=MOMENT
    )


def test_summary_of_a_purchase_and_a_sale_follows_the_statement() -> None:
    summary = summarize([sale(), purchase()])

    assert summary.total_spent == Decimal("38.85")
    assert summary.total_received == Decimal("35.70")
    assert summary.total_fees == Decimal("2.15")
    assert summary.total_penalties == Decimal("4.00")
    assert summary.total_profit == Decimal("3.00")


def test_summary_of_sales_only_has_nothing_spent() -> None:
    summary = summarize([sale()])

    assert summary.total_spent == Decimal("0.00")
    assert summary.total_received == Decimal("35.70")
    assert summary.total_fees == Decimal("0.30")


def test_summary_of_purchases_only_has_nothing_received() -> None:
    summary = summarize([purchase(), purchase("28.00", "0.00")])

    assert summary.total_spent == Decimal("66.85")
    assert summary.total_received == Decimal("0.00")
    assert summary.total_fees == Decimal("1.85")
    assert summary.total_penalties == Decimal("0.00")
    assert summary.total_profit == Decimal("0.00")


def test_summary_without_transactions_is_all_zero() -> None:
    summary = summarize([])

    zero = Decimal("0.00")
    assert (
        summary.total_spent,
        summary.total_received,
        summary.total_fees,
        summary.total_penalties,
        summary.total_profit,
    ) == (zero, zero, zero, zero, zero)


def test_summary_keeps_the_sign_of_the_profit() -> None:
    summary = summarize([sale(), sale("42.50", "50.00", "8.50")])

    assert summary.total_profit == Decimal("-4.50")
    assert summary.total_penalties == Decimal("12.50")
    assert summary.total_received == Decimal("69.70")
