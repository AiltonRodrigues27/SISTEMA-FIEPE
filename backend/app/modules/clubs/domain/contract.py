from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import StrEnum

from app.shared.domain.rounding import round_half_up

MAX_PENALTY = Decimal("10.00")
SHORT_TERM_MAX_DAYS = 30
MEDIUM_TERM_MAX_DAYS = 180
SHORT_TERM_PENALTY_PERCENT = 5
MEDIUM_TERM_PENALTY_PERCENT = 10
LONG_TERM_PENALTY_PERCENT = 20


class ContractStatus(StrEnum):
    ATIVO = "ATIVO"
    ENCERRADO = "ENCERRADO"
    RESCINDIDO = "RESCINDIDO"


@dataclass(frozen=True)
class Contract:
    id: int | None
    player_id: int
    club_id: int
    purchase_value: Decimal
    loyalty_until: datetime
    status: ContractStatus
    started_at: datetime
    ended_at: datetime | None


def remaining_days(loyalty_until: datetime, now: datetime) -> int:
    remaining = loyalty_until - now
    if remaining <= timedelta(0):
        return 0
    whole_days, rest = divmod(remaining, timedelta(days=1))
    return whole_days + (1 if rest else 0)


def penalty_percent(days: int) -> int:
    if days == 0:
        return 0
    if days <= SHORT_TERM_MAX_DAYS:
        return SHORT_TERM_PENALTY_PERCENT
    if days <= MEDIUM_TERM_MAX_DAYS:
        return MEDIUM_TERM_PENALTY_PERCENT
    return LONG_TERM_PENALTY_PERCENT


def calculate_penalty(market_value: Decimal, days: int) -> Decimal:
    penalty = round_half_up(market_value * penalty_percent(days) / 100, 2)
    return min(penalty, MAX_PENALTY)
