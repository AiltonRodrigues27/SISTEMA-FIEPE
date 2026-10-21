from typing import Annotated

from fastapi import APIRouter, Depends, Response

from app.api.dependencies import (
    build_buy_player,
    build_list_transactions,
    build_sell_player,
    parse_resource_id,
)
from app.modules.market.adapters.inbound.http.csv_export import build_transactions_csv
from app.modules.market.adapters.inbound.http.list_query import get_transaction_filters
from app.modules.market.adapters.inbound.http.schemas import (
    BuyPlayerRequest,
    PurchaseResponse,
    SaleResponse,
    TransactionHistoryResponse,
)
from app.modules.market.application.buy_player import BuyPlayer
from app.modules.market.application.list_transactions import ListTransactions
from app.modules.market.application.sell_player import SellPlayer
from app.modules.market.domain.history import TransactionFilters

router = APIRouter(tags=["Mercado"])


@router.post("/players/{player_id}/buy")
def buy_player(
    player_id: str,
    body: BuyPlayerRequest,
    use_case: Annotated[BuyPlayer, Depends(build_buy_player)],
) -> PurchaseResponse:
    result = use_case.execute(parse_resource_id(player_id), body.club_id, body.loyalty_until)
    return PurchaseResponse.from_result(result)


@router.post("/players/{player_id}/sell")
def sell_player(
    player_id: str,
    use_case: Annotated[SellPlayer, Depends(build_sell_player)],
) -> SaleResponse:
    return SaleResponse.from_result(use_case.execute(parse_resource_id(player_id)))


@router.get("/clubs/{club_id}/transactions")
def list_transactions(
    club_id: str,
    filters: Annotated[TransactionFilters, Depends(get_transaction_filters)],
    use_case: Annotated[ListTransactions, Depends(build_list_transactions)],
) -> TransactionHistoryResponse:
    history = use_case.execute(parse_resource_id(club_id), filters)
    return TransactionHistoryResponse.from_history(history)


@router.get("/clubs/{club_id}/transactions/export")
def export_transactions(
    club_id: str,
    filters: Annotated[TransactionFilters, Depends(get_transaction_filters)],
    use_case: Annotated[ListTransactions, Depends(build_list_transactions)],
) -> Response:
    history = use_case.execute(parse_resource_id(club_id), filters)
    return Response(
        content=build_transactions_csv(history.transactions),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="transacoes-clube-{club_id}.csv"'},
    )
