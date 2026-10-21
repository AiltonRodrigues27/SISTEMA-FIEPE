from datetime import datetime
from decimal import Decimal

from app.modules.market.domain.calculations import calculate_sale_outcome
from app.modules.market.domain.transaction import Transaction, TransactionType
from app.shared.domain.brasilia_time import BRASILIA

MOMENT = datetime(2026, 11, 2, 10, 15, tzinfo=BRASILIA)


def test_purchase_takes_the_value_and_the_fee_out_of_the_cash() -> None:
    transaction = Transaction.purchase(
        club_id=1,
        player_id=2,
        player_name="Meia Lua",
        value=Decimal("37.00"),
        fee=Decimal("1.85"),
        created_at=MOMENT,
    )

    assert transaction.type is TransactionType.COMPRA
    assert transaction.id is None
    assert transaction.penalty == Decimal("0.00")
    assert transaction.profit is None
    assert transaction.cash_change == Decimal("-38.85")


def test_sale_records_the_commission_as_fee_and_the_credit_as_cash_change() -> None:
    outcome = calculate_sale_outcome(Decimal("40.00"), Decimal("37.00"), Decimal("4.00"))

    transaction = Transaction.sale(
        club_id=1, player_id=2, player_name="Meia Lua", outcome=outcome, created_at=MOMENT
    )

    assert transaction.type is TransactionType.VENDA
    assert transaction.value == Decimal("40.00")
    assert transaction.fee == Decimal("0.30")
    assert transaction.penalty == Decimal("4.00")
    assert transaction.profit == Decimal("3.00")
    assert transaction.cash_change == Decimal("35.70")
    assert transaction.created_at == MOMENT
