from typing import Annotated

from fastapi import APIRouter, Depends, Response

from app.api.dependencies import (
    build_buy_player,
    build_list_transactions,
    build_sell_player,
    parse_resource_id,
)
from app.api.error_docs import error_responses
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

CSV_RESPONSE = {
    200: {
        "description": "Arquivo CSV em UTF-8, sem BOM, com ponto e vírgula como separador.",
        "content": {"text/csv": {"schema": {"type": "string"}}},
    }
}


@router.post(
    "/players/{player_id}/buy",
    summary="Compra um jogador livre",
    responses=error_responses(400, 404, 409),
)
def buy_player(
    player_id: str,
    body: BuyPlayerRequest,
    use_case: Annotated[BuyPlayer, Depends(build_buy_player)],
) -> PurchaseResponse:
    """
    Compra um jogador livre para um clube.

    - O preço é o **valor de mercado** do momento, mais 5% de taxa quando ele passa de 30,00.
    - O custo total (valor + taxa) não pode passar de **50% do caixa** do clube, sem arredondar.
    - O elenco tem no máximo 12 jogadores.
    - `loyalty_until`: fim da fidelidade, no formato `AAAA-MM-DDTHH:MM-03:00`, depois do momento
      da compra e em até 1.095 dias.
    - O clube não recompra um jogador que ele mesmo vendeu; outros clubes podem comprá-lo.

    Numa única operação, a compra desconta o caixa, coloca o jogador no elenco, abre o contrato
    `ATIVO` e grava a transação `COMPRA`. Uma compra recusada não grava nada.

    Erros: `400` (corpo ou `club_id` inválido, data fora do formato ou da janela), `404` (jogador
    ou clube inexistente) e `409` (jogador com clube, limite do caixa, elenco cheio ou recompra).
    """
    result = use_case.execute(parse_resource_id(player_id), body.club_id, body.loyalty_until)
    return PurchaseResponse.from_result(result)


@router.post(
    "/players/{player_id}/sell",
    summary="Vende um jogador do elenco",
    responses=error_responses(404, 409),
)
def sell_player(
    player_id: str,
    use_case: Annotated[SellPlayer, Depends(build_sell_player)],
) -> SaleResponse:
    """
    Vende o jogador pelo clube em que ele está, pelo **valor de mercado** do momento. Não tem
    corpo.

    - **Multa por fidelidade:** os dias restantes até o fim da fidelidade são arredondados para
      cima. 0 dia: sem multa; 1 a 30: 5%; 31 a 180: 10%; 181 ou mais: 20%. A multa é limitada a
      10,00.
    - **Comissão:** só sobre o lucro (valor de mercado menos o valor de compra): 10% da parte até
      10,00 e 20% da parte acima.
    - **Crédito no caixa** = valor de mercado - multa - comissão.
    - O contrato passa a `RESCINDIDO` (com multa) ou `ENCERRADO` (sem multa), o jogador volta a
      ser livre e a transação `VENDA` é gravada na mesma operação.

    Erros: `404` (jogador inexistente, mal formado ou excluído) e `409` (jogador livre).
    """
    return SaleResponse.from_result(use_case.execute(parse_resource_id(player_id)))


@router.get(
    "/clubs/{club_id}/transactions",
    summary="Histórico de transações do clube",
    responses=error_responses(400, 404),
)
def list_transactions(
    club_id: str,
    filters: Annotated[TransactionFilters, Depends(get_transaction_filters)],
    use_case: Annotated[ListTransactions, Depends(build_list_transactions)],
) -> TransactionHistoryResponse:
    """
    Lista as compras e as vendas do clube, da mais recente para a mais antiga (empate: maior id
    primeiro), com o nome e os valores do momento de cada uma.

    Parâmetros de consulta, opcionais e combináveis:

    - `type`: `COMPRA`, `VENDA` ou os dois separados por vírgula, sem espaços e sem repetir.
    - `player_id`: só as transações desse jogador no clube.

    A resposta traz `data` e `summary` (`total_spent`, `total_received`, `total_fees`,
    `total_penalties` e `total_profit`), que respeita os mesmos filtros. Sem transações, `data`
    vem vazio e o `summary` zerado. As transações de jogador excluído continuam na lista.

    Erros: `400` (filtro inválido, vazio ou repetido) e `404` (clube inexistente, ou jogador do
    filtro inexistente ou excluído).
    """
    history = use_case.execute(parse_resource_id(club_id), filters)
    return TransactionHistoryResponse.from_history(history)


@router.get(
    "/clubs/{club_id}/transactions/export",
    summary="Exporta o histórico de transações em CSV",
    response_class=Response,
    responses={**CSV_RESPONSE, **error_responses(400, 404)},
)
def export_transactions(
    club_id: str,
    filters: Annotated[TransactionFilters, Depends(get_transaction_filters)],
    use_case: Annotated[ListTransactions, Depends(build_list_transactions)],
) -> Response:
    """
    Exporta o histórico do clube em CSV, com os mesmos filtros (`type` e `player_id`) e a mesma
    ordem do histórico.

    - Colunas: `data_hora;tipo;jogador;valor;taxa_ou_comissao;multa;lucro;variacao_caixa`.
    - Separador `;`, valores com 2 casas e vírgula decimal, `lucro` vazio na compra.
    - Nome com `;` ou aspas vai entre aspas duplas, e cada aspa interna é duplicada.
    - UTF-8 sem BOM, cada linha termina em `\\n`. Sem transações, só o cabeçalho.

    Erros (sempre em JSON): `400` (filtro inválido) e `404` (clube ou jogador do filtro
    inexistente).
    """
    history = use_case.execute(parse_resource_id(club_id), filters)
    return Response(
        content=build_transactions_csv(history.transactions),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="transacoes-clube-{club_id}.csv"'},
    )
