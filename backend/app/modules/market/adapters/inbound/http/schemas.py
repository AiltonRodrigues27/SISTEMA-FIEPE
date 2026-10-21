from typing import Self

from pydantic import BaseModel

from app.api.strict_types import BrasiliaDateTime, ResourceId
from app.modules.market.application.buy_player import PurchaseResult
from app.modules.market.application.list_transactions import TransactionHistory
from app.modules.market.application.sell_player import SaleResult
from app.modules.market.domain.history import TransactionSummary
from app.modules.market.domain.transaction import Transaction
from app.shared.domain.brasilia_time import format_api_datetime


class BuyPlayerRequest(BaseModel):
    club_id: ResourceId
    loyalty_until: BrasiliaDateTime


class TransactionResponse(BaseModel):
    id: int
    club_id: int
    player_id: int
    player_name: str
    type: str
    value: float
    fee: float
    penalty: float
    profit: float | None
    cash_change: float
    created_at: str

    @classmethod
    def from_transaction(cls, transaction: Transaction) -> Self:
        return cls(
            id=transaction.id,
            club_id=transaction.club_id,
            player_id=transaction.player_id,
            player_name=transaction.player_name,
            type=transaction.type.value,
            value=float(transaction.value),
            fee=float(transaction.fee),
            penalty=float(transaction.penalty),
            profit=float(transaction.profit) if transaction.profit is not None else None,
            cash_change=float(transaction.cash_change),
            created_at=format_api_datetime(transaction.created_at),
        )


class PurchaseContractResponse(BaseModel):
    purchase_value: float
    loyalty_until: str
    status: str


class PurchaseResponse(TransactionResponse):
    contract: PurchaseContractResponse
    club_cash: float

    @classmethod
    def from_result(cls, result: PurchaseResult) -> Self:
        transaction = TransactionResponse.from_transaction(result.transaction)
        contract = PurchaseContractResponse(
            purchase_value=float(result.contract.purchase_value),
            loyalty_until=format_api_datetime(result.contract.loyalty_until),
            status=result.contract.status,
        )
        return cls(**transaction.model_dump(), contract=contract, club_cash=float(result.club_cash))


class SaleResponse(TransactionResponse):
    purchase_value: float
    remaining_days: int
    penalty_rate: int
    contract_status: str
    club_cash: float

    @classmethod
    def from_result(cls, result: SaleResult) -> Self:
        transaction = TransactionResponse.from_transaction(result.transaction)
        termination = result.termination
        return cls(
            **transaction.model_dump(),
            purchase_value=float(termination.purchase_value),
            remaining_days=termination.remaining_days,
            penalty_rate=termination.penalty_percent,
            contract_status=termination.status,
            club_cash=float(result.club_cash),
        )


class SummaryResponse(BaseModel):
    total_spent: float
    total_received: float
    total_fees: float
    total_penalties: float
    total_profit: float

    @classmethod
    def from_summary(cls, summary: TransactionSummary) -> Self:
        return cls(
            total_spent=float(summary.total_spent),
            total_received=float(summary.total_received),
            total_fees=float(summary.total_fees),
            total_penalties=float(summary.total_penalties),
            total_profit=float(summary.total_profit),
        )


class TransactionHistoryResponse(BaseModel):
    data: list[TransactionResponse]
    summary: SummaryResponse

    @classmethod
    def from_history(cls, history: TransactionHistory) -> Self:
        return cls(
            data=[TransactionResponse.from_transaction(item) for item in history.transactions],
            summary=SummaryResponse.from_summary(history.summary),
        )
