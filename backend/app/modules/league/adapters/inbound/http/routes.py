from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status

from app.api.dependencies import (
    build_get_lineup,
    build_get_match,
    build_get_standings,
    build_list_matches,
    build_play_match,
    build_set_lineup,
    parse_resource_id,
)
from app.api.error_docs import error_responses
from app.modules.league.adapters.inbound.http.list_query import get_match_club_id
from app.modules.league.adapters.inbound.http.schemas import (
    LineupResponse,
    MatchResponse,
    MatchSummaryResponse,
    PlayMatchRequest,
    SetLineupRequest,
    StandingsRowResponse,
)
from app.modules.league.application.get_lineup import GetLineup
from app.modules.league.application.get_match import GetMatch
from app.modules.league.application.get_standings import GetStandings
from app.modules.league.application.list_matches import ListMatches
from app.modules.league.application.play_match import PlayMatch
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


@router.post(
    "/matches",
    status_code=status.HTTP_201_CREATED,
    summary="Joga uma partida",
    responses=error_responses(400, 404, 409),
)
def play_match(
    body: PlayMatchRequest,
    request: Request,
    response: Response,
    use_case: Annotated[PlayMatch, Depends(build_play_match)],
) -> MatchResponse:
    """
    Joga uma partida na hora entre dois clubes com a escalação completa e grava o resultado. Não
    há sorteio: com os mesmos titulares, nas mesmas condições, o resultado é sempre o mesmo.

    - **Duelos:** são sempre 6. Nos duelos 1 a 3 o mandante ataca; nos 4 a 6, o visitante. Os
      jogadores de linha são numerados pela ordem do elenco, do 1º (o mais recuado) ao 4º (o mais
      avançado). Em cada lado, o 4º ataca o goleiro, o 3º ataca o 1º e o 2º ataca o 2º do
      adversário.
    - **Valores:** o atacante usa o atributo da posição dele (`shooting` no `ATA`, `passing` no
      `MEI` e `dribbling` no `ZAG` e no `LAT`) e o defensor usa sempre `defending`. Um titular
      `MAL_CONDICIONADO` joga com 15% a menos em cada atributo (arredondado; o meio sobe).
    - **Gol:** quando o valor do ataque é **maior** que o da defesa. Duelo empatado não é gol.
    - **Resultado:** `result` é `MANDANTE`, `VISITANTE` ou `EMPATE`, pelos gols de cada clube
      (de 0 a 3).
    - A partida grava a data e a hora, o placar, as formações e os 6 duelos, com os nomes, as
      posições, as condições e os valores do momento. Não muda o caixa, a escalação nem os
      jogadores, e pode se repetir quantas vezes for.

    Responde `201` com o cabeçalho `Location`.

    Erros: `400` (`home_club_id` ou `away_club_id` ausente ou inválido, ou os dois iguais), `404`
    (clube inexistente) e `409` (algum dos clubes sem a escalação completa). Em qualquer erro,
    nada é gravado.
    """
    view = use_case.execute(body.home_club_id, body.away_club_id)
    response.headers["Location"] = request.url_for("get_match", match_id=view.match.id).path
    return MatchResponse.from_view(view)


@router.get(
    "/matches",
    summary="Histórico de partidas",
    responses=error_responses(400, 404),
)
def list_matches(
    club_id: Annotated[int | None, Depends(get_match_club_id)],
    use_case: Annotated[ListMatches, Depends(build_list_matches)],
) -> list[MatchSummaryResponse]:
    """
    Lista as partidas da mais recente para a mais antiga (empate de data e hora: maior id
    primeiro), com o placar e o `result`, **sem** os duelos.

    Parâmetro de consulta opcional:

    - `club_id`: só as partidas em que o clube foi mandante ou visitante. Inteiro positivo, só
      com dígitos.

    Erros: `400` (`club_id` inválido ou vazio) e `404` (clube inexistente).
    """
    return [MatchSummaryResponse.from_view(view) for view in use_case.execute(club_id)]


@router.get(
    "/matches/{match_id}",
    summary="Consulta uma partida com os duelos",
    responses=error_responses(404),
)
def get_match(
    match_id: str,
    use_case: Annotated[GetMatch, Depends(build_get_match)],
) -> MatchResponse:
    """
    Consulta uma partida com os 6 duelos, na ordem (1 a 3: ataques do mandante; 4 a 6: ataques do
    visitante). Os nomes, as posições, as condições e os valores são os do momento da partida.

    Erros: `404` (partida inexistente ou id mal formado).
    """
    return MatchResponse.from_view(use_case.execute(parse_resource_id(match_id)))


@router.get("/standings", summary="Classificação")
def get_standings(
    use_case: Annotated[GetStandings, Depends(build_get_standings)],
) -> list[StandingsRowResponse]:
    """
    Classificação com **todos** os clubes, inclusive os que ainda não jogaram (zerados). Ela é
    calculada a cada consulta, nunca gravada.

    - Vitória vale 3 pontos, empate 1 e derrota 0.
    - Ordem: mais pontos; depois maior saldo de gols; depois mais gols marcados; depois o nome do
      clube, em ordem alfabética (sem diferenciar maiúsculas e acentos); depois o id.
    - `position` vai de 1 ao total de clubes, sem repetir.
    """
    return [StandingsRowResponse.from_row(row) for row in use_case.execute()]
