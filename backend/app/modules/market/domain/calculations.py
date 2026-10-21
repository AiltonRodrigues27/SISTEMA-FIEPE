from dataclasses import dataclass
from decimal import Decimal

from app.modules.market.domain.errors import CashLimitExceeded
from app.shared.domain.rounding import round_half_up

ZERO = Decimal("0.00")
FEE_PERCENT = Decimal(5)
FEE_MIN_MARKET_VALUE = Decimal("30.00")
CASH_LIMIT_DIVISOR = 2
COMMISSION_FIRST_BAND_LIMIT = Decimal("10.00")
COMMISSION_FIRST_BAND_PERCENT = Decimal(10)
COMMISSION_SECOND_BAND_PERCENT = Decimal(20)


@dataclass(frozen=True)
class SaleOutcome:
    value: Decimal
    penalty: Decimal
    profit: Decimal
    commission: Decimal
    credit: Decimal


def calculate_purchase_fee(market_value: Decimal) -> Decimal:
    if market_value <= FEE_MIN_MARKET_VALUE:
        return ZERO
    return round_half_up(market_value * FEE_PERCENT / 100, 2)


def ensure_within_cash_limit(total_cost: Decimal, cash: Decimal) -> None:
    if total_cost * CASH_LIMIT_DIVISOR > cash:
        raise CashLimitExceeded("O custo total não pode passar de 50% do caixa do clube.")


def calculate_commission(profit: Decimal) -> Decimal:
    if profit <= 0:
        return ZERO
    first_band = min(profit, COMMISSION_FIRST_BAND_LIMIT)
    second_band = profit - first_band
    commission = (
        first_band * COMMISSION_FIRST_BAND_PERCENT / 100
        + second_band * COMMISSION_SECOND_BAND_PERCENT / 100
    )
    return round_half_up(commission, 2)


def calculate_sale_outcome(
    market_value: Decimal, purchase_value: Decimal, penalty: Decimal
) -> SaleOutcome:
    profit = market_value - purchase_value
    commission = calculate_commission(profit)
    return SaleOutcome(
        value=market_value,
        penalty=penalty,
        profit=profit,
        commission=commission,
        credit=market_value - penalty - commission,
    )
