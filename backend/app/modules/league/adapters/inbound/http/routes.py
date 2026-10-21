from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import build_get_lineup, build_set_lineup, parse_resource_id
from app.api.error_docs import error_responses
from app.modules.league.adapters.inbound.http.schemas import LineupResponse, SetLineupRequest
from app.modules.league.application.get_lineup import GetLineup
from app.modules.league.application.set_lineup import SetLineup

router = APIRouter(tags=["Liga"])


@router.put(
    "/clubs/{club_id}/lineup",
    summary="Escala os titulares do clube",
    responses=error_responses(400, 404, 409),
)
def set_lineup(
    club_id: str,
    body: SetLineupRequest,
    use_case: Annotated[SetLineup, Depends(build_set_lineup)],
) -> LineupResponse:
    """
    Escolhe a formação e os 5 titulares do clube. A escalação anterior é **substituída por
    inteiro**, numa única operação.

    - `formation`: `3-1`, `2-2`, `2-1-1` ou `1-2-1` (os números contam os jogadores de linha,
      de trás para frente, sem o goleiro: defesa, meio e ataque).
    - `player_ids`: exatamente 5 ids inteiros positivos e distintos, em qualquer ordem.
    - As posições precisam fechar a formação: 1 `GOL` e, em cada setor, a quantidade da
      formação (defesa = `ZAG` ou `LAT`, meio = `MEI`, ataque = `ATA`).
    - Os titulares precisam ser do elenco do clube e não podem estar `DOENTE`. Um jogador
      `MAL_CONDICIONADO` pode ser escalado.
    - Escalar não muda o caixa.

    A resposta traz `players` na ordem do elenco (GOL, ZAG, LAT, MEI, ATA), com os mesmos campos
    de `GET /players/{id}`.

    Erros: `400` (`formation` ou `player_ids` ausente ou fora do formato), `404` (clube ou
    jogador inexistente, inclusive excluído) e `409` (jogador fora do elenco, `DOENTE` ou
    posições que não fecham a formação). Em qualquer erro, nada é gravado.
    """
    details = use_case.execute(parse_resource_id(club_id), body.formation, body.player_ids)
    return LineupResponse.from_details(details)


@router.get(
    "/clubs/{club_id}/lineup",
    summary="Consulta a escalação do clube",
    responses=error_responses(404),
)
def get_lineup(
    club_id: str,
    use_case: Annotated[GetLineup, Depends(build_get_lineup)],
) -> LineupResponse:
    """
    Consulta a escalação atual do clube.

    - Sem escalação: `formation` nula, `players` vazio e `complete` falso.
    - `complete` é verdadeiro quando há os 5 titulares.
    - Quando um titular é vendido ou fica `DOENTE`, ele sai da escalação: a `formation` continua a
      salva, `players` traz os titulares que sobraram e `complete` fica falso até o clube escalar
      de novo. O jogador não volta sozinho.

    Erros: `404` (clube inexistente ou id mal formado).
    """
    return LineupResponse.from_details(use_case.execute(parse_resource_id(club_id)))
