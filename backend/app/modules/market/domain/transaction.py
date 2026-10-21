from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Self

from app.modules.market.domain.calculations import ZERO, SaleOutcome


class TransactionType(StrEnum):
    COMPRA = "COMPRA"
    VENDA = "VENDA"


@dataclass(frozen=True)
class Transaction:
    id: int | None
    club_id: int
    player_id: int
    player_name: str
    type: TransactionType
    value: Decimal
    fee: Decimal
    penalty: Decimal
    profit: Decimal | None
    cash_change: Decimal
    created_at: datetime

    @classmethod
    def purchase(
        cls,
        *,
        club_id: int,
        player_id: int,
        player_name: str,
        value: Decimal,
        fee: Decimal,
        created_at: datetime,
    ) -> Self:
        return cls(
            id=None,
            club_id=club_id,
            player_id=player_id,
            player_name=player_name,
            type=TransactionType.COMPRA,
            value=value,
            fee=fee,
            penalty=ZERO,
            profit=None,
            cash_change=-(value + fee),
            created_at=created_at,
        )

    @classmethod
    def sale(
        cls,
        *,
        club_id: int,
        player_id: int,
        player_name: str,
        outcome: SaleOutcome,
        created_at: datetime,
    ) -> Self:
        return cls(
            id=None,
            club_id=club_id,
            player_id=player_id,
            player_name=player_name,
            type=TransactionType.VENDA,
            value=outcome.value,
            fee=outcome.commission,
            penalty=outcome.penalty,
            profit=outcome.profit,
            cash_change=outcome.credit,
            created_at=created_at,
        )
