from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import build_buy_player, build_sell_player, parse_resource_id
from app.modules.market.adapters.inbound.http.schemas import (
    BuyPlayerRequest,
    PurchaseResponse,
    SaleResponse,
)
from app.modules.market.application.buy_player import BuyPlayer
from app.modules.market.application.sell_player import SellPlayer

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
