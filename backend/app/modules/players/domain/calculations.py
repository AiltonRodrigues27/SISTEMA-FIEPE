from decimal import Decimal

from app.modules.players.domain.entities import Attributes
from app.modules.players.domain.enums import PhysicalCondition, Position
from app.shared.domain.rounding import round_half_up

MIN_MONEY_VALUE = Decimal("1.00")
YOUNG_PROMISE_MAX_AGE = 21
YOUNG_ADJUSTMENT_PERCENT = Decimal(10)
SENIOR_MIN_AGE = 32
SENIOR_ADJUSTMENT_PERCENT = Decimal(-10)
TOTAL_PERCENT_FLOOR = Decimal(-40)

CONDITION_DISCOUNT_PERCENT = {
    PhysicalCondition.APTO: Decimal(0),
    PhysicalCondition.MAL_CONDICIONADO: Decimal(15),
    PhysicalCondition.DOENTE: Decimal(30),
}
HIGH_AGILITY_MIN = 80
LOW_AGILITY_MAX = 30
LOW_AGILITY_EXTRA_DISCOUNT = Decimal(10)

# A ordem das colunas é a dos campos de Attributes: pace, shooting, passing, dribbling,
# defending, physical.
OVERALL_WEIGHTS: dict[Position, tuple[int, int, int, int, int, int]] = {
    Position.GOL: (10, 0, 20, 0, 40, 30),
    Position.ZAG: (10, 0, 15, 0, 45, 30),
    Position.LAT: (25, 0, 20, 15, 25, 15),
    Position.MEI: (10, 15, 35, 25, 5, 10),
    Position.ATA: (20, 40, 10, 20, 0, 10),
}

# (overall onde a faixa começa, onde termina, valor de cada ponto dentro da faixa)
BASE_VALUE_BANDS = (
    (40, 60, Decimal("0.50")),
    (60, 75, Decimal("2.00")),
    (75, 99, Decimal("6.00")),
)


def calculate_overall(position: Position, attributes: Attributes) -> int:
    weights = OVERALL_WEIGHTS[position]
    weighted_sum = sum(value * weight for value, weight in zip(attributes, weights, strict=True))
    return int(round_half_up(Decimal(weighted_sum) / 100, 0))


def calculate_base_value(overall: int, potential: int, age_at_registration: int) -> Decimal:
    overall_part = _overall_part(overall)
    if age_at_registration <= YOUNG_PROMISE_MAX_AGE:
        overall_part = overall_part * (100 + potential - overall) / 100
    return max(round_half_up(overall_part, 2), MIN_MONEY_VALUE)


def calculate_market_value(
    base_value: Decimal, condition: PhysicalCondition, agility: int, age: int
) -> Decimal:
    total_percent = max(
        _age_adjustment_percent(age) - _condition_discount_percent(condition, agility),
        TOTAL_PERCENT_FLOOR,
    )
    market_value = round_half_up(base_value * (100 + total_percent) / 100, 2)
    return max(market_value, MIN_MONEY_VALUE)


def _overall_part(overall: int) -> Decimal:
    total = Decimal(0)
    for band_start, band_end, value_per_point in BASE_VALUE_BANDS:
        points_in_band = max(0, min(overall, band_end) - band_start)
        total += points_in_band * value_per_point
    return total


def _condition_discount_percent(condition: PhysicalCondition, agility: int) -> Decimal:
    discount = CONDITION_DISCOUNT_PERCENT[condition]
    if condition is PhysicalCondition.APTO:
        return discount
    if agility >= HIGH_AGILITY_MIN:
        return discount / 2
    if agility <= LOW_AGILITY_MAX:
        return discount + LOW_AGILITY_EXTRA_DISCOUNT
    return discount


def _age_adjustment_percent(age: int) -> Decimal:
    if age <= YOUNG_PROMISE_MAX_AGE:
        return YOUNG_ADJUSTMENT_PERCENT
    if age >= SENIOR_MIN_AGE:
        return SENIOR_ADJUSTMENT_PERCENT
    return Decimal(0)
