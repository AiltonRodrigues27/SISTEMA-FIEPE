from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from decimal import Decimal
from enum import StrEnum
from typing import Self

from app.modules.clubs.domain.errors import InvalidLoyaltyDate
from app.shared.domain.rounding import round_half_up

MAX_LOYALTY_DAYS = 1095
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

    @classmethod
    def open(
        cls,
        *,
        player_id: int,
        club_id: int,
        purchase_value: Decimal,
        loyalty_until: datetime,
        now: datetime,
    ) -> Self:
        if not now < loyalty_until <= now + timedelta(days=MAX_LOYALTY_DAYS):
            raise InvalidLoyaltyDate(
                f"O fim da fidelidade deve ser depois de agora e em até {MAX_LOYALTY_DAYS} dias."
            )
        return cls(
            id=None,
            player_id=player_id,
            club_id=club_id,
            purchase_value=purchase_value,
            loyalty_until=loyalty_until,
            status=ContractStatus.ATIVO,
            started_at=now,
            ended_at=None,
        )

    def close(self, now: datetime, penalty: Decimal) -> Self:
        status = ContractStatus.RESCINDIDO if penalty > 0 else ContractStatus.ENCERRADO
        return replace(self, status=status, ended_at=now)


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
