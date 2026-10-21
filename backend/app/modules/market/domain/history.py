from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from decimal import Decimal

from app.modules.market.domain.calculations import ZERO
from app.modules.market.domain.transaction import Transaction, TransactionType


@dataclass(frozen=True)
class TransactionFilters:
    types: tuple[TransactionType, ...] | None = None
    player_id: int | None = None


@dataclass(frozen=True)
class TransactionSummary:
    total_spent: Decimal
    total_received: Decimal
    total_fees: Decimal
    total_penalties: Decimal
    total_profit: Decimal


def summarize(transactions: Sequence[Transaction]) -> TransactionSummary:
    purchases = [item for item in transactions if item.type is TransactionType.COMPRA]
    sales = [item for item in transactions if item.type is TransactionType.VENDA]
    return TransactionSummary(
        total_spent=_total(item.value + item.fee for item in purchases),
        total_received=_total(item.cash_change for item in sales),
        total_fees=_total(item.fee for item in transactions),
        total_penalties=_total(item.penalty for item in sales),
        total_profit=_total(item.profit for item in sales),
    )


def _total(values: Iterable[Decimal]) -> Decimal:
    return sum(values, ZERO)
